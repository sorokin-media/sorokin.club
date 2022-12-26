const initHideLinks = () => {
    const hideLinks = document.querySelectorAll('[data-href]');
    if (!hideLinks.length) return;

    const removeClasses = ['hlink'];

    hideLinks.forEach((link) => {
        const href = atob(link.dataset.href);
        let inlineClasses = [...link.classList].filter(cl => removeClasses.indexOf(cl) === -1);

        inlineClasses = inlineClasses.length ? `class="${inlineClasses.join(' ')}"` : '';

        link.outerHTML = `
        <a href="${ href }" ${ inlineClasses }>
            ${ link.innerHTML }
        </a>`;
    });
};
document.addEventListener("DOMContentLoaded", function () {
  initHideLinks();
});
