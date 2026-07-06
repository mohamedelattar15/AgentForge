# AgentForge — Adapter Trace OpenTelemetry
# Implémente TracePort via OpenTelemetry (OTLP).

from datetime import datetime, timezone

from agentforge_core.ports.trace_port import TracePort
from agentforge_core.types import Span

try:
    from opentelemetry import trace as otel_trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
except ImportError:
    otel_trace = None  # type: ignore
    Resource = None
    TracerProvider = None
    BatchSpanProcessor = None
    OTLPSpanExporter = None


class OTelTrace(TracePort):
    """Trace OpenTelemetry — exporte les traces au format OTLP.

    Compatible avec Jaeger, Zipkin, Grafana Tempo, et tout backend OTLP.
    """

    def __init__(
        self,
        service_name: str = "agentforge",
        endpoint: str = "http://localhost:4317",
        headers: dict | None = None,
    ) -> None:
        """Initialise le traceur OpenTelemetry.

        Args:
            service_name: Nom du service (ressource).
            endpoint: Endpoint OTLP gRPC (ex: "http://jaeger:4317").
            headers: En-têtes personnalisés pour l'exporteur.
        """
        if otel_trace is None:
            raise ImportError(
                "opentelemetry est requis. Installez : pip install "
                "opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp-proto-grpc"
            )

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)

        exporter = OTLPSpanExporter(
            endpoint=endpoint,
            headers=headers or {},
        )
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

        otel_trace.set_tracer_provider(provider)
        self._tracer = otel_trace.get_tracer(service_name)

    async def record(self, run_id: str, spans: list[Span]) -> None:
        """Enregistre une trace via OpenTelemetry.

        Args:
            run_id: Identifiant du run.
            spans: Liste des spans d'exécution.
        """
        with self._tracer.start_as_current_span(f"run-{run_id[:8]}") as root_span:
            root_span.set_attribute("run.id", run_id)
            root_span.set_attribute("span.count", len(spans))

            for span_data in spans:
                with self._tracer.start_as_current_span(
                    span_data.name,
                    start_time=self._to_nano(span_data.start_time),
                ) as child_span:
                    for key, value in span_data.attributes.items():
                        child_span.set_attribute(f"agentforge.{key}", str(value))
                    child_span.end(end_time=self._to_nano(span_data.end_time))

    @staticmethod
    def _to_nano(dt: datetime) -> int:
        """Convertit un datetime en nanosecondes (format OTel).

        Args:
            dt: Datetime à convertir.

        Returns:
            int: Timestamp en nanosecondes.
        """
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        delta = dt - epoch
        return int(delta.total_seconds() * 1_000_000_000)
