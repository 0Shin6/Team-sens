document.addEventListener("DOMContentLoaded", function() {    
    const API_BASE = "http://127.0.0.1:3000/api";

    const newsData = [
        {
            img: "img/logo.jpg", 
            desc: "Bienvenue sur notre site officiel #SensTouch"
        },
        {
            img: "img/maillot.png", 
            desc: "La Team Sens remporte le tournoi d'hiver !"
        },
        {
            img: "img/valorant.png",
            desc: "Les recrutements sont ouverts pour le roster Valorant."
        }
    ];

    const fallbackMatchesData = [
        {
            teamA: "img/logo-seul.png", 
            teamB: "img/logo-seul.png",
            date: "22/09",
            heure: "21h",
            jeu: "Valorant"
        },
        {
            teamA: "img/logo-seul.png",
            teamB: "img/logo-seul.png",
            date: "25/09",
            heure: "20h30",
            jeu: "Rocket League"
        }
    ];

    async function getMatchesData() {
        try {
            const response = await fetch(`${API_BASE}/matches`);
            if (!response.ok) {
                return fallbackMatchesData;
            }

            const data = await response.json();
            if (!Array.isArray(data) || data.length === 0) {
                return fallbackMatchesData;
            }

            return data.map((item) => {
                const dateText = typeof item.date === "string" ? item.date : "";
                const [datePart, heurePart] = dateText.split(" ", 2);
                return {
                    teamA: item.teamA || "img/logo-seul.png",
                    teamB: item.teamB || "img/logo-seul.png",
                    date: datePart || dateText || "A definir",
                    heure: heurePart || "A definir",
                    jeu: item.jeu || "Inconnu"
                };
            });
        } catch (error) {
            return fallbackMatchesData;
        }
    }

    function setupSlider(data, containerType) {
        let currentIndex = 0;
        
        const dotsContainer = document.getElementById(`${containerType}-dots`);
        const contentContainer = document.getElementById(`${containerType}-slider`);

        dotsContainer.innerHTML = "";
        data.forEach((_, index) => {
            const dot = document.createElement("span");
            dot.classList.add("dot");
            if (index === 0) dot.classList.add("active");
            
            dot.addEventListener("click", () => {
                currentIndex = index;
                updateDisplay(currentIndex);
                resetAutoSlide();
            });
            
            dotsContainer.appendChild(dot);
        });

        function updateDisplay(index) {
            contentContainer.classList.remove("fade-anim");
            void contentContainer.offsetWidth;
            contentContainer.classList.add("fade-anim");

            if (containerType === "news") {
                document.getElementById("news-img").src = data[index].img;
                document.getElementById("news-desc").textContent = data[index].desc;
            } else if (containerType === "match") {
                document.getElementById("match-team-a").src = data[index].teamA;
                document.getElementById("match-team-b").src = data[index].teamB;
                document.getElementById("match-date").textContent = data[index].date;
                document.getElementById("match-heure").textContent = data[index].heure;
                document.getElementById("match-game").textContent = data[index].jeu;
            }

            const dots = dotsContainer.querySelectorAll(".dot");
            dots.forEach(d => d.classList.remove("active"));
            dots[index].classList.add("active");
        }

        let autoSlideInterval;
        
        function startAutoSlide() {
            autoSlideInterval = setInterval(() => {
                currentIndex = (currentIndex + 1) % data.length;
                updateDisplay(currentIndex);
            }, 5000); 
        }

        function resetAutoSlide() {
            clearInterval(autoSlideInterval);
            startAutoSlide();
        }
        updateDisplay(0);
        startAutoSlide();
    }

    if(document.getElementById("news-slider")) {
        setupSlider(newsData, "news");
    }
    
    if(document.getElementById("match-slider")) {
        getMatchesData().then((matches) => {
            setupSlider(matches, "match");
        });
    }

    const contactForm = document.querySelector(".contact-form");
    if (contactForm) {
        const statusEl = document.getElementById("contact-status");
        const endpoint = contactForm.getAttribute("data-endpoint");

        contactForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (!endpoint) {
                if (statusEl) statusEl.textContent = "Endpoint manquant.";
                return;
            }

            const email = document.getElementById("contact-email").value.trim();
            const nom = document.getElementById("contact-nom").value.trim();
            const discord = document.getElementById("contact-discord").value.trim();
            const objet = document.getElementById("contact-objet").value.trim();
            const message = document.getElementById("contact-message").value.trim();

            if (!email || !nom || !objet || !message) {
                if (statusEl) statusEl.textContent = "Merci de remplir tous les champs obligatoires.";
                return;
            }

            const payload = {
                email,
                nom,
                discord: discord || null,
                objet,
                message
            };

            if (statusEl) statusEl.textContent = "Envoi en cours...";

            try {
                const res = await fetch(endpoint, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await res.json().catch(() => null);

                if (res.ok) {
                    if (statusEl) statusEl.textContent = "Message envoyé !";
                    contactForm.reset();
                } else {
                    if (statusEl) statusEl.textContent = (data && data.message) ? data.message : "Erreur lors de l'envoi.";
                }
            } catch (err) {
                if (statusEl) statusEl.textContent = "Erreur réseau.";
            }
        });
    }

});