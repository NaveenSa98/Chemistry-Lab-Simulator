class API {
    static async getChemicalColor(name) {
        try {
            const response = await fetch(`http://localhost:5000/api/chemical-color/${encodeURIComponent(name)}`);
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    }

    static async react(ingredients, temperature = 'room', concentration = 'dilute') {
        try {
            const response = await fetch('http://localhost:5000/api/react', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ingredients,
                    temperature,
                    concentration
                })
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    }

    static async getExplanation(reactionData) {
        try {
            const response = await fetch('http://localhost:5000/api/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reaction_data: reactionData })
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    }
}
