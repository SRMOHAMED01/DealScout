"""
DealScout - Resilient Kafka Client & Abstraction
Palier A.2 / A.3

Features:
- Standard EventEnvelope serialization
- Automatic Dead Letter Queue (DLQ) routing on malformed payloads
- Configurable retries and graceful shutdown
- Seamless fallback to InMemoryKafkaBus when running offline or in unit tests
"""

from __future__ import annotations

import json
import logging
import socket
import time
from collections import defaultdict
from typing import Any, Callable

from ingestion.config import config
from ingestion.models import EventEnvelope

logger = logging.getLogger(__name__)

try:
    from confluent_kafka import Producer as ConfluentProducer, KafkaException
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False


def is_kafka_reachable(bootstrap_servers: str, timeout: float = 0.5) -> bool:
    """Proactively checks whether Kafka TCP port is listening."""
    try:
        endpoint = bootstrap_servers.split(",")[0].strip()
        if ":" in endpoint:
            host, port_str = endpoint.split(":")
            port = int(port_str)
        else:
            host, port = endpoint, 9092
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


class InMemoryKafkaBus:
    """
    In-memory message bus for local testing, offline demo, and mock tests.
    Stores messages partitioned by topic.
    """
    def __init__(self) -> None:
        self.topics: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def publish(self, topic: str, key: str | None, value: dict[str, Any]) -> None:
        self.topics[topic].append({
            "key": key,
            "value": value,
            "published_at": time.time(),
        })

    def get_messages(self, topic: str) -> list[dict[str, Any]]:
        return list(self.topics.get(topic, []))

    def clear(self) -> None:
        self.topics.clear()


# Global in-memory bus for mock/test mode
in_memory_bus = InMemoryKafkaBus()


class DealScoutProducer:
    """
    Unified, reliable Kafka producer with automatic envelope wrapping and DLQ fallback.
    """

    def __init__(
        self,
        bootstrap_servers: str | None = None,
        mock_mode: bool = False,
        retries: int = 3,
    ) -> None:
        self.bootstrap_servers = bootstrap_servers or config.kafka_bootstrap_servers
        self.mock_mode = mock_mode or (not KAFKA_AVAILABLE)
        self.retries = retries
        self._producer: Any = None

        if not self.mock_mode and KAFKA_AVAILABLE:
            if not is_kafka_reachable(self.bootstrap_servers):
                logger.info("Kafka broker offline at %s, using resilient in-memory bus", self.bootstrap_servers)
                self.mock_mode = True
            else:
                try:
                    conf = {
                        "bootstrap.servers": self.bootstrap_servers,
                        "retries": self.retries,
                        "socket.timeout.ms": 2000,
                        "message.timeout.ms": 3000,
                        "linger.ms": 10,
                    }
                    self._producer = ConfluentProducer(conf)
                    logger.info("Connected to Kafka at %s", self.bootstrap_servers)
                except Exception as err:
                    logger.warning("Kafka connection failed (%s), switching to in-memory mock", err)
                    self.mock_mode = True

    def build_envelope(
        self,
        payload: dict[str, Any],
        event_type: str,
        source: str,
    ) -> EventEnvelope:
        """Wraps payload into standard DealScout EventEnvelope."""
        return EventEnvelope(
            event_type=event_type,
            source=source,
            payload=payload,
        )

    def send_event(
        self,
        topic: str,
        key: str,
        payload: dict[str, Any],
        event_type: str,
        source: str,
    ) -> EventEnvelope:
        """
        Serializes and produces an event to Kafka.
        Routes to DLQ if validation or serialization fails.
        """
        try:
            envelope = self.build_envelope(payload, event_type, source)
            serialized = envelope.model_dump_json()

            # Always record to in-memory bus for local downstream pipeline consumers
            in_memory_bus.publish(topic, key, json.loads(serialized))

            if not self.mock_mode and self._producer is not None:
                self._producer.produce(
                    topic=topic,
                    key=key.encode("utf-8") if key else None,
                    value=serialized.encode("utf-8"),
                    on_delivery=self._delivery_report,
                )
                self._producer.poll(0)

            return envelope

        except Exception as exc:
            logger.error("Failed to produce event to %s: %s. Routing to DLQ.", topic, exc)
            self.send_to_dlq(topic, key, payload, str(exc))
            raise

    def send_to_dlq(
        self,
        original_topic: str,
        key: str,
        raw_payload: Any,
        error_reason: str,
    ) -> None:
        """
        Sends rejected or malformed events to a Dead Letter Queue topic.
        """
        dlq_topic = f"{original_topic}-dlq"
        dlq_record = {
            "original_topic": original_topic,
            "key": key,
            "raw_payload": raw_payload,
            "error": error_reason,
            "timestamp": time.time(),
        }

        if self.mock_mode or self._producer is None:
            in_memory_bus.publish(dlq_topic, key, dlq_record)
        else:
            try:
                self._producer.produce(
                    topic=dlq_topic,
                    key=key.encode("utf-8") if key else None,
                    value=json.dumps(dlq_record).encode("utf-8"),
                )
                self._producer.poll(0)
            except Exception as dlq_err:
                logger.critical("Failed to write to DLQ %s: %s", dlq_topic, dlq_err)

    def _delivery_report(self, err: Any, msg: Any) -> None:
        if err is not None:
            logger.error("Message delivery failed: %s", err)

    def flush(self, timeout: float = 5.0) -> None:
        if self._producer and not self.mock_mode:
            self._producer.flush(timeout)

    def close(self) -> None:
        self.flush()
