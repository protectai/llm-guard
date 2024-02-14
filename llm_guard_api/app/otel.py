from fastapi import FastAPI
from opentelemetry import metrics, propagate, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.propagators.aws import AwsXRayPropagator
from opentelemetry.sdk.extension.aws.resource.ec2 import AwsEc2ResourceDetector
from opentelemetry.sdk.extension.aws.trace import AwsXRayIdGenerator
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import (
    SERVICE_NAME,
    SERVICE_VERSION,
    Resource,
    get_aggregated_resources,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from .config import MetricsConfig, TracingConfig
from .version import __version__


def _configure_tracing(tracing_config: TracingConfig, resource: Resource) -> None:
    if tracing_config is None:
        return

    if tracing_config.exporter == "xray":
        propagate.set_global_textmap(AwsXRayPropagator())
        resource = resource.merge(
            get_aggregated_resources(
                [AwsEc2ResourceDetector()],
            )
        )

    tracer_provider = TracerProvider(resource=resource)
    if tracing_config.exporter == "xray":
        tracer_provider.id_generator = AwsXRayIdGenerator()
        exporter = OTLPSpanExporter(endpoint=tracing_config.endpoint)
    elif tracing_config.exporter == "otel_http":
        exporter = OTLPSpanExporter(endpoint=tracing_config.endpoint)
    elif tracing_config.exporter == "console":
        exporter = ConsoleSpanExporter()

    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(tracer_provider)


def _configure_metrics(metrics_config: MetricsConfig, resource: Resource) -> None:
    if metrics_config is None:
        return

    if metrics_config.exporter == "console":
        reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
    elif metrics_config.exporter == "otel_http":
        reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=metrics_config.endpoint))
    elif metrics_config.exporter == "prometheus":
        reader = PrometheusMetricReader()

    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)


def configure_otel(
    app_name: str, tracing_config: TracingConfig, metrics_config: MetricsConfig
) -> None:
    resource = Resource(
        attributes={
            SERVICE_NAME: app_name,
            SERVICE_VERSION: __version__,
        }
    )

    _configure_tracing(tracing_config, resource)
    _configure_metrics(metrics_config, resource)


def instrument_app(app: FastAPI) -> None:
    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls="healthz,readyz,metrics",
        meter_provider=metrics.get_meter_provider(),
        tracer_provider=trace.get_tracer_provider(),
    )
