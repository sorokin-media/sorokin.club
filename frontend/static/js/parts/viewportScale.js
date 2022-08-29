document.addEventListener("DOMContentLoaded", function () {

    const body = document.querySelector('body');
    const isScaleblePage = document.querySelector('#mobile-scale-page');
    const viewportMetaTag = document.querySelector('meta[name="viewport"]');

    if (isScaleblePage) {
        initViewportScale(viewportMetaTag, isScaleblePage.dataset.mobileWidth);
    }

    function initViewportScale (viewport, breakpoint) {
        const defaultViewportContent = 'width=device-width,height=device-height,initial-scale=1.0';

        if (window.innerWidth > breakpoint) {
            viewport.setAttribute('content', defaultViewportContent);
            return
        }

        const initialScale = window.screen.width / window.innerWidth;
        const newViewportContent = `width=device-width,height=device-height,initial-scale=${initialScale},maximum-scale=${initialScale},user-scalable=no`;

        viewport.setAttribute('content', newViewportContent);
    }
});
