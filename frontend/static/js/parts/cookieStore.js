const curUrl = new URL(window.location);

// Utm_source
const urlUtm = curUrl.searchParams.get('utm_source') || '';

if (get_cookie('utm_source') !== urlUtm && urlUtm.length > 0) {
    document.cookie = `utm_source=${ urlUtm }`;
}

// Referrer
const referrerList = [
    'yandex',
    'google',
    'rambler',
    'yahoo',
    'mail',
];
let curReferrer = document.referrer;

if (curReferrer.length && !get_cookie('utm_source')) {

    curReferrer = new URL(curReferrer).hostname.split('.');

    if (curReferrer.length > 1)  {
        curReferrer = curReferrer[curReferrer.length - 2];
    } else {
        curReferrer = curReferrer[0];
    }

    const isReferrerInList = referrerList.indexOf(curReferrer) !== -1 ? true : false;

    if (isReferrerInList && get_cookie('search_referrer') !== curReferrer.toUpperCase()) {
        document.cookie = 'search_referrer=' + curReferrer.toUpperCase();
    }
}


function get_cookie ( cookie_name ) {
    var results = document.cookie.match ( '(^|;) ?' + cookie_name + '=([^;]*)(;|$)' );

    if ( results ) {
        return ( unescape ( results[2] ) );
    } else {
        return null;
    }
}
