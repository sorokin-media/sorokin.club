const windowHeight = document.documentElement.clientHeight;

const getLazySourcesPos = (elements) => {
    const positions = [];

    elements.forEach(element => {
        positions.push(element.getBoundingClientRect().top + pageYOffset);
    });

    return positions;
}
const lazyLoadSource = (el) => {
    const attrName = el.dataset.src ? 'src' : el.dataset.srcset ? 'srcset' : '';
    if (!attrName.length) return;

    const srcToLoad = el.dataset[attrName];

    el.setAttribute(attrName, srcToLoad);
    el.removeAttribute(`data-${attrName}`);
}
const checkLazyLoadPositions = (positions, elements, offset = 0) => {
    if (!positions.length || !elements.length) return;

    const loadElIndexes = [];
    positions.forEach((pos, index) => pageYOffset > pos - windowHeight - offset ? loadElIndexes.push(index) : '');

    if (!loadElIndexes.length) return;

    loadElIndexes.forEach(elIndex => {
        lazyLoadSource(elements[elIndex]);
        delete positions[elIndex];
    })
}

const initLazyLoading = () => {
    const lazySources = document.querySelectorAll('img[data-src],source[data-srcset]');
    const lazyPositions = getLazySourcesPos(lazySources);

    window.addEventListener('scroll', () => {
        checkLazyLoadPositions(lazyPositions, lazySources, 150);
    });
    checkLazyLoadPositions(lazyPositions, lazySources, 150);
}

export default initLazyLoading;
