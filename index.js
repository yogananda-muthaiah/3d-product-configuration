// --- script.js (Conceptual Three.js/JavaScript) ---

const API_URL = 'http://127.0.0.1:8000/configure';
let chairModel; // Assume this holds the loaded GLTF scene (a Three.js Object3D)

// Function to find a mesh/node by its name in the glTF hierarchy
function findComponent(name) {
    return chairModel.getObjectByName(name);
}

// Function to execute the instructions received from the Python API
function applyConfig(configData) {
    const updateList = configData.update_list;
    
    updateList.forEach(instruction => {
        const component = findComponent(instruction.component_id);

        if (!component) {
            console.warn(`Component not found: ${instruction.component_id}`);
            return;
        }

        switch (instruction.property_name) {
            case 'baseColorFactor':
                // For color, we target the mesh's material and update its color property.
                if (component.material) {
                    const [r, g, b, a] = instruction.value;
                    component.material.color.setRGB(r, g, b);
                    // In glTF, baseColorFactor includes alpha, but Three.js uses color for RGB.
                    console.log(`Color set for ${instruction.component_id} to RGB(${r}, ${g}, ${b})`);
                }
                break;

            case 'visible':
                // For structure, we hide or show the entire node/group.
                component.visible = instruction.value;
                console.log(`Visibility set for ${instruction.component_id} to ${instruction.value}`);
                break;
                
            // Add more cases for texture changes, transformations, etc.
        }
    });

    document.getElementById('price-display').textContent = `Total Price: $${configData.final_price}`;
}

// --- Main function to send request and update model ---
async function updateProductConfiguration(color, legCount) {
    const requestPayload = {
        seat_color: color,
        leg_style: legCount
    };

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestPayload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const configData = await response.json();
        
        // --- KEY STEP: Apply the instructions from the Python API ---
        applyConfig(configData);

    } catch (error) {
        console.error("Error fetching or applying configuration:", error);
    }
}

// --- Example Usage (simulating user interaction) ---
// This call will configure the chair to be blue with 4 legs, driven by the Python API.
// updateProductConfiguration("Blue", 4);
