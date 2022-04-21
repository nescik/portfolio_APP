var macy =  Macy({
    
    container: '.gallery',
    trueOrder: false,
    waitForImages: false,
    margin: 20,
    breakAt: {
        1200: 2,
        940: 3,
        520: 2,
        400: 1
    },

});


window.addEventListener("scroll", () => {
    const nav = document.querySelector("nav");

    nav.classList.toggle("navbarsticky", window.scrollY > 500);
})

 




