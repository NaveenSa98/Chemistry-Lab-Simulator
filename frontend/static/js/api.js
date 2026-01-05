class API {
    // Auto-detect API base URL: use current origin in production, localhost in development
    static getBaseURL() {
        // If running on localhost, use localhost:5000
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:5000';
        }
        // Otherwise use the current origin (Railway URL)
        return window.location.origin;
    }

    static async getChemicalColor(name) {
        try {
            const response = await fetch(`${this.getBaseURL()}/api/chemical-color/${encodeURIComponent(name)}`);
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    }

    static async react(ingredients, temperature = 'room', concentration = 'dilute') {
        try {
            const response = await fetch(`${this.getBaseURL()}/api/react`, {
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
            const response = await fetch(`${this.getBaseURL()}/api/explain`, {
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
