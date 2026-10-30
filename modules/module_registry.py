from dataclasses import dataclass

@dataclass(frozen=True)
class Module:
    id: str
    title: str
    description: str
    icon: str
    status: str = "Active"

MODULES=(
 Module("home","Home Dashboard","Campus guide overview and operational status","🏛️"),
 Module("assistant","AI Campus Assistant","Ask questions grounded in attached campus documents","💬"),
 Module("explorer","Campus Explorer","Ask for clear answers about locations and facilities from campus sources","🔎"),
 Module("navigation","Campus Navigation","Get source-grounded, step-by-step directions with verification caveats","🧭"),
 Module("library","Library Assistant","Ask about the Law and Technical Libraries, facilities, and directions","📚"),
 Module("transport","University Transport","Ask about university bus routes, fees, pickup times, and transport procedures","🚌"),
 Module("about","About the System","Learn how the guide works and ask questions about its features","ℹ️"),
)
