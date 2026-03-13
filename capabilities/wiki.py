from __future__ import annotations
import wikipedia

class WikipediaCapability:
    def __init__(self, language: str = "de") -> None:
        wikipedia.set_lang(language)

    def get_summary(self, topic: str, sentences: int = 3) -> str:
        cleaned_topic = topic.strip()
        if not cleaned_topic:
            return "Ich habe kein Thema für Wikipedia erkannt."

        try:
            return wikipedia.summary(cleaned_topic, sentences=sentences)
        except wikipedia.exceptions.DisambiguationError as exc:
            suggestions = ", ".join(exc.options[:5])
            return (
                f"Der Begriff {cleaned_topic} ist nicht eindeutig. "
                f"Mögliche Themen sind: {suggestions}."
            )
        except wikipedia.exceptions.PageError:
            return f"Ich habe keinen Wikipedia-Artikel zu {cleaned_topic} gefunden."
        except Exception as exc:
            return f"Beim Abruf von Wikipedia ist ein Fehler aufgetreten: {exc}"