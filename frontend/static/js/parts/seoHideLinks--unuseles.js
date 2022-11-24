function base64_decode( data ) {
    let b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    let o1, o2, o3, h1, h2, h3, h4, bits, i=0, enc='';
    do {
        h1 = b64.indexOf(data.charAt(i++));
        h2 = b64.indexOf(data.charAt(i++));
        h3 = b64.indexOf(data.charAt(i++));
        h4 = b64.indexOf(data.charAt(i++));
        bits = h1<<18 | h2<<12 | h3<<6 | h4;
        o1 = bits>>16 & 0xff;
        o2 = bits>>8 & 0xff;
        o3 = bits & 0xff;

        if (h3 == 64) enc += String.fromCharCode(o1);
        else if (h4 == 64) enc += String.fromCharCode(o1, o2);
        else enc += String.fromCharCode(o1, o2, o3);
    } while (i < data.length);
    return enc;
}

function replaceHLink() {
    const links = document.querySelectorAll('.post-text a[href]');

    links.forEach((link) => {
        const attrs = [...link.attributes];
        const arr = attrs.map((attr) => {
            if (attr.name != 'data-href') {
                return `${ attr.name } + '="' + attr.value + '"`;
            }
        })

        const replaceLink = `
            <a ${ arr.join(' ') } href="${ base64_decode($(this).data("href")) }">
                ${ link.innerHTML }
            </a>
        `;

        // $(this).replaceWith('<a ' + arr.join(' ') + ' href="'
        // + base64_decode($(this).data("href")) + '">' + $(this).html() + '</a>');
    });
};

document.addEventListener("DOMContentLoaded", function () {
    replaceHLink();
});
