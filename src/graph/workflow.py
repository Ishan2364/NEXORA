from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver 
from langchain_core.messages import RemoveMessage # <--- NEW IMPORT
from src.graph.state import AgentState
from src.agents.supervisor import supervisor_node
from src.agents.worker_agents import (
    open_secure_payment_form, recommendation_node, inventory_node, loyalty_node, 
    payment_node, fulfillment_node, post_purchase_node
)

# Import all tools
from src.agents.worker_agents import (
    check_inventory_status, search_catalog, calculate_final_price,
    get_customer_profile, find_products, search_products, 
    get_product_details_for_comparison, get_cross_sell_products,
    request_back_in_stock_notification, update_inventory_stock,
    calculate_final_pricing, get_active_promotions,
    process_card_payment, generate_upi_qr, add_to_cart,
    create_fulfillment_order, schedule_home_delivery, generate_invoice, 
    schedule_instore_pickup, get_order_status, query_rag_tool_doc, 
    process_refund, request_human_assistance , generate_invoice 
)

def create_retail_graph():
    workflow = StateGraph(AgentState)

    # --- NEW: HISTORY TRIMMER NODE ---
    def trim_history(state):
        messages = state["messages"]
        # Keep only the last 15 messages to keep it fast
        if len(messages) > 15:
            return {"messages": [RemoveMessage(id=m.id) for m in messages[:-15]]}
        return {}

    workflow.add_node("trimmer", trim_history)
    # ---------------------------------

    # 1. Add Nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("RecommendationAgent", recommendation_node)
    workflow.add_node("InventoryAgent", inventory_node)
    workflow.add_node("LoyaltyAndOffersAgent", loyalty_node)
    workflow.add_node("PaymentAgent", payment_node)
    workflow.add_node("FulfillmentAgent", fulfillment_node)
    workflow.add_node("PostPurchaseSupportAgent", post_purchase_node)

    # 2. Add Tools
    all_tools = [
        check_inventory_status, search_catalog, calculate_final_price,
        get_customer_profile, find_products, search_products, 
        get_product_details_for_comparison, get_cross_sell_products,
        request_back_in_stock_notification, update_inventory_stock,
        calculate_final_pricing, get_active_promotions,
        process_card_payment, generate_upi_qr, add_to_cart,
        create_fulfillment_order, schedule_home_delivery, generate_invoice,
        schedule_instore_pickup, get_order_status, query_rag_tool_doc, 
        process_refund, request_human_assistance , open_secure_payment_form 
        
    ]
    workflow.add_node("tools", ToolNode(all_tools))

    # 3. Define Edges
    # START -> TRIMMER -> SUPERVISOR
    workflow.add_edge(START, "trimmer")
    workflow.add_edge("trimmer", "supervisor")

    # Supervisor -> Next Agent
    workflow.add_conditional_edges(
        "supervisor",
        lambda x: x["next"], 
    )

    # Agent -> Tools OR End
    members = ["RecommendationAgent", "InventoryAgent", "LoyaltyAndOffersAgent", "PaymentAgent", "FulfillmentAgent", "PostPurchaseSupportAgent"]
    
    for member in members:
        workflow.add_conditional_edges(
            member,
            tools_condition,
            {
                "tools": "tools",
                END: END
            }
        )

    # Tools -> Back to Sender
    def route_tool_output(state):
        return state["sender"]

    workflow.add_conditional_edges(
        "tools",
        route_tool_output
    )

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)