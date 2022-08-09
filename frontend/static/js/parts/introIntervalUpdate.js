const introStartForm = document.getElementById('intro-start-form');

if (introStartForm) {

    const introFormUpdateDelay = 15 * 1000;
    const startIntroDataUpdate = updateFormData(introStartForm, {
        url: '/intro/',
        method: 'PUT',
        async: true,
    });

    setInterval(() => {
        startIntroDataUpdate();
    }, introFormUpdateDelay);

}

function updateFormData (form, { url = '/', method = 'PUT', async = true }) {
    let oldData = undefined;

    return wrapper;

    function wrapper () {
        const body = Object.values(form).reduce(
            (obj, field) => {
                obj[field.name] = field.value;
                return obj;
            }, {}
        );

        if (JSON.stringify(body) === JSON.stringify(oldData)) {
            return;
        }

        // Put request
        const putRequest = new XMLHttpRequest();
        putRequest.open(method, url, async);
        putRequest.send(JSON.stringify(body));

        oldData = body;
    }
}
