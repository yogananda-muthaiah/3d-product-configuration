from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import os

app = FastAPI(title="3D Product Configurator API")

# Enable CORS for browser requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def serve_index():
    """Serve the index.html file"""
    return FileResponse("index.html")

@app.get("/chair.glb")
async def serve_chair_model():
    """Serve the chair 3D model"""
    return FileResponse("chair.glb", media_type="model/gltf-binary")

# --- 1. Define the Input Schema ---
# This is what the client sends to the API
class ConfigRequest(BaseModel):
    seat_color: str
    leg_style: int

# --- 2. Define the Output Schema (Instructions for the Viewer) ---
# This tells the 3D viewer what to change on the loaded GLTF model
class UpdateInstruction(BaseModel):
    component_id: str
    property_name: str
    value: Any

class ConfigResponse(BaseModel):
    update_list: List[UpdateInstruction]
    final_price: float = 0.00

@app.post("/configure", response_model=ConfigResponse)
def configure_product(request: ConfigRequest):
    """
    Processes the user's configuration and returns instructions for the 3D viewer.
    """
    update_instructions = []
    final_price = 100.00 # Base Price

    # --- Configuration Logic for SEAT COLOR ---
    # Maps simple color names to glTF PBR baseColorFactor (RGBA list)
    color_map = {
        "original": None,  # Keep original color
        "blue": ([0.0, 0.0, 1.0, 1.0], 20.00),
        "red": ([1.0, 0.0, 0.0, 1.0], 15.00),
        "green": ([0.0, 0.8, 0.0, 1.0], 15.00),
        "yellow": ([1.0, 1.0, 0.0, 1.0], 10.00),
        "black": ([0.1, 0.1, 0.1, 1.0], 25.00),
        "white": ([1.0, 1.0, 1.0, 1.0], 20.00),
        "grey": ([0.5, 0.5, 0.5, 1.0], 10.00),
        "brown": ([0.55, 0.27, 0.07, 1.0], 15.00),
        "orange": ([1.0, 0.5, 0.0, 1.0], 12.00),
    }
    
    color_choice = request.seat_color.lower()
    
    # Only add color change instruction if not original
    if color_choice != "original" and color_choice in color_map:
        color_rgba, price_add = color_map[color_choice]
        final_price += price_add
        
        # Instruction: Change the color of all chair meshes
        update_instructions.append(
            UpdateInstruction(
                component_id="ALL_MESHES",
                property_name="baseColorFactor",
                value=color_rgba
            )
        )
    elif color_choice == "original":
        # Keep original - send instruction to reset to original
        update_instructions.append(
            UpdateInstruction(
                component_id="ALL_MESHES",
                property_name="baseColorFactor",
                value="original"  # Special value to indicate original color
            )
        )

    # --- Configuration Logic for LEG STYLE (Show/Hide) ---
    # Ensures only the selected leg style is visible.
    
    # Instruction 2: Hide 3-Leg group by default
    update_instructions.append(
        UpdateInstruction(
            component_id="Legs_3_Group",
            property_name="visible",
            value=False
        )
    )
    # Instruction 3: Hide 4-Leg group by default
    update_instructions.append(
        UpdateInstruction(
            component_id="Legs_4_Group",
            property_name="visible",
            value=False
        )
    )

    # Instruction 4: Show the requested leg group
    if request.leg_style == 4:
        update_instructions.append(
            UpdateInstruction(
                component_id="Legs_4_Group",
                property_name="visible",
                value=True
            )
        )
        final_price += 50.00
    elif request.leg_style == 3:
        update_instructions.append(
            UpdateInstruction(
                component_id="Legs_3_Group",
                property_name="visible",
                value=True
            )
        )
        final_price += 30.00
    
    # Return the complete set of instructions
    return ConfigResponse(
        update_list=update_instructions,
        final_price=round(final_price, 2)
    )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

