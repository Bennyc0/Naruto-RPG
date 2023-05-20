const sizes = [1, 1, 2, 3, 4];

function Position(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

const body = document.querySelector(".body");

for (let i = 0; i < 20; i++) {
    const top = Position(1, 100);
    const left = Position(1, 100);
    const random = Math.floor(Math.random() * sizes.length);
    const randomSize = sizes[random];
    const div = document.createElement('div');
    div.style.position = 'absolute';
    div.style.top = top + '%';
    div.style.left = left + '%';
    div.style.height = randomSize + 'px';
    div.style.width = randomSize + 'px';
    div.classList.add('star');
    document.body.appendChild(div);
}