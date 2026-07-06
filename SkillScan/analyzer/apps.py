from django.apps import AppConfig


class AnalyzerConfig(AppConfig):
    name = 'analyzer'
    def ready(self):
        import analyzer.signals
