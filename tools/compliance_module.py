from .compliance_tool.retriever import check_compliance

def compliance_check(message: str) -> str:
    return check_compliance(message)


def compliance_node(state):
    message = state.get("compliance_text", "")
    if message:
        result = check_compliance(message)
        state["compliance_result"] = result
    else:
        state["compliance_result"] = "No compliance text provided."
    return state