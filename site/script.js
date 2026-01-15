document.addEventListener("DOMContentLoaded", function() {    
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

    const matchesData = [
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
        setupSlider(matchesData, "match");
    }

});