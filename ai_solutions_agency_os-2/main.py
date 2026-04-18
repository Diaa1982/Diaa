from __future__ import annotations

import json
from pathlib import Path

from ai_solutions_agency.workflow import build_graph
from ai_solutions_agency.state import create_initial_state


def main() -> None:
    root = Path(__file__).parent
    sample_file = root / "examples" / "sample_deal.json"
    with sample_file.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    state = create_initial_state(
        customer_name=payload["customer_name"],
        customer_input_raw=payload["customer_input_raw"],
        industry=payload.get("industry", "unknown"),
        company_size=payload.get("company_size", "unknown"),
        geo=payload.get("geo", "unknown"),
        currency=payload.get("currency", "USD"),
    )

    graph = build_graph()
    result = graph.invoke(
        state,
        config={"configurable": {"thread_id": payload.get("deal_id", "demo-thread-1")}},
    )

    output_path = root / "run_output.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("Run completed.")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()
