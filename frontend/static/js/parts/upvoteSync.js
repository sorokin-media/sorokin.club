let upvoteSyncs = [];
let upvoteObserver = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        synchronizeUpvote(mutation.target.parentElement, mutation.target.textContent);
    });
});

setTimeout(() => {
    upvoteSyncs = document.querySelectorAll('.upvote-sync .upvote');

    if (upvoteSyncs.length > 1) {
        startUpvoteObserve(upvoteSyncs);
    }

}, 500)

function startUpvoteObserve(elems) {

    for (let i = 0; i < elems.length; i++) {
        const elem = elems[i];

        upvoteObserver.observe(
            elem,
            {
                characterData: true,
                childList: true,
                subtree: true,
            }
        )
    }

}

function synchronizeUpvote(target, targetValue) {
    const value = targetValue.toString().replace(/\s/gm, '');
    const wrapper = target.closest('.upvote-sync');
    const allBtns = wrapper.querySelectorAll('.upvote');

    upvoteObserver.disconnect();

    for (let i = 0; i < allBtns.length; i++) {
        const btn = allBtns[i];

        if (btn === target) {
            console.log('continue');
            continue;
        }

        btn.classList = target.classList;
        btn.innerHTML = value;
    }

    location.reload();
}
