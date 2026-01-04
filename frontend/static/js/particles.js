class Particle {
    constructor(x, y, type, color) {
        this.pos = createVector(x, y);
        if (type === 'bubble') {
            this.vel = createVector(random(-0.5, 0.5), random(-1, -3));
        } else if (type === 'precipitate') {
            this.vel = createVector(random(-0.2, 0.2), random(0.5, 1.5));
        } else if (type === 'deposition') {
            this.vel = createVector(random(-0.1, 0.1), random(0.5, 1.2));
            this.settled = false;
        } else if (type === 'heat') {
            this.vel = createVector(random(-0.3, 0.3), random(-0.5, -1.5));
        } else {
            this.vel = createVector(random(-1, 1), random(-1, 1));
        }
        this.acc = createVector(0, 0);
        this.lifespan = 255;
        this.type = type; // 'bubble', 'precipitate', 'heat', 'deposition'
        this.color = color || [255, 255, 255];
        this.size = type === 'bubble' ? random(4, 10) : (type === 'heat' ? random(10, 20) : random(3, 6));
        this.wobbleOffset = random(1000);
    }

    update() {
        if (this.type === 'bubble') {
            this.acc.x = map(noise(this.wobbleOffset + frameCount * 0.1), 0, 1, -0.05, 0.05);
            this.vel.add(this.acc);
            this.pos.add(this.vel);
        } else if (this.type === 'precipitate') {
            this.pos.add(this.vel);
        } else if (this.type === 'deposition') {
            if (!this.settled) {
                this.pos.add(this.vel);
                if (this.pos.y > (beakerY + beakerH - random(10, 20))) {
                    this.settled = true;
                    this.vel.mult(0);
                }
            } else {
                // Stay at bottom, flicker slightly
                this.pos.x += random(-0.1, 0.1);
            }
        } else if (this.type === 'heat') {
            this.pos.add(this.vel);
            this.lifespan -= 4;
        }

        // Deposition particles live longer once settled
        if (this.type === 'deposition' && this.settled) {
            this.lifespan -= 0.5;
        } else {
            if (this.type !== 'heat') this.lifespan -= 2;
        }
    }

    show() {
        noStroke();
        if (this.type === 'bubble') {
            fill(255, 255, 255, this.lifespan * 0.3);
            ellipse(this.pos.x, this.pos.y, this.size);
            noFill();
            stroke(255, 255, 255, this.lifespan * 0.6);
            ellipse(this.pos.x, this.pos.y, this.size);
        } else if (this.type === 'heat') {
            fill(255, 255, 255, this.lifespan * 0.1);
            ellipse(this.pos.x, this.pos.y, this.size);
            // Add a bit of transparency/blur feel
            fill(255, 255, 255, this.lifespan * 0.05);
            ellipse(this.pos.x, this.pos.y, this.size * 1.5);
        } else {
            fill(this.color[0], this.color[1], this.color[2], this.lifespan);
            ellipse(this.pos.x, this.pos.y, this.size);
        }
    }

    isDead() {
        if (this.type === 'bubble' || this.type === 'heat') {
            let surface = beakerY + beakerH - liquidLevel;
            return this.lifespan < 0 || this.pos.y < surface;
        }
        return this.lifespan < 0 || this.pos.y > (beakerY + beakerH - 10);
    }
}

class ParticleSystem {
    constructor() {
        this.particles = [];
        this.active = false;
        this.type = 'bubble';
        this.color = [255, 255, 255];
    }

    addParticle(x, y) {
        if (this.active) {
            this.particles.push(new Particle(x, y, this.type, this.color));
        }
    }

    run() {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            let p = this.particles[i];
            p.update();
            p.show();
            if (p.isDead()) {
                this.particles.splice(i, 1);
            }
        }
    }

    setType(type, color) {
        this.type = type;
        this.color = color;
        this.active = true;
    }

    stop() {
        this.active = false;
    }
}
