const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const gridSize = 20;
const gridWidth = canvas.width / gridSize;
const gridHeight = canvas.height / gridSize;

let snake = [{x: 10, y: 10}];
let direction = 'right';
let food = {x: Math.floor(Math.random() * gridWidth), y: Math.floor(Math.random() * gridHeight)};
let score = 0;

function findSafePath() {
    const start = {x: snake[0].x, y: snake[0].y};
    const target = {x: food.x, y: food.y};
    const visited = new Set();
    const queue = [{pos: start, path: []}];
    visited.add(`${start.x},${start.y}`);

    while (queue.length > 0) {
        const {pos, path} = queue.shift();
        if (pos.x === target.x && pos.y === target.y) {
            return path;
        }

        const directions = ['up', 'down', 'left', 'right'];
        for (const dir of directions) {
            const nextPos = {x: pos.x, y: pos.y};
            switch (dir) {
                case 'up': nextPos.y--; break;
                case 'down': nextPos.y++; break;
                case 'left': nextPos.x--; break;
                case 'right': nextPos.x++; break;
            }

            // 检查边界
            if (nextPos.x < 0 || nextPos.x >= gridWidth || nextPos.y < 0 || nextPos.y >= gridHeight) {
                continue;
            }

            // 检查是否为蛇身（排除尾部）
            const isSnakeBody = snake.some(seg => seg.x === nextPos.x && seg.y === nextPos.y);
            const tail = snake[snake.length - 1];
            if (isSnakeBody && (nextPos.x !== tail.x || nextPos.y !== tail.y)) {
                continue;
            }

            const key = `${nextPos.x},${nextPos.y}`;
            if (!visited.has(key)) {
                visited.add(key);
                queue.push({pos: nextPos, path: [...path, dir]});
            }
        }
    }
    return null;
}

function calculateDirection() {
    const path = findSafePath();
    if (path && path.length > 0) {
        direction = path[0];
        return;
    }

    const head = snake[0];
    const dx = food.x - head.x;
    const dy = food.y - head.y;

    const checkDirection = (dir) => {
        const newHead = {...head};
        switch (dir) {
            case 'up': newHead.y--; break;
            case 'down': newHead.y++; break;
            case 'left': newHead.x--; break;
            case 'right': newHead.x++; break;
        }
        for (let i = 0; i < snake.length; i++) {
            if (snake[i].x === newHead.x && snake[i].y === newHead.y) {
                return false;
            }
        }
        return true;
    };

    if (dx > 0 && direction !== 'left' && checkDirection('right')) {
        direction = 'right';
    } else if (dx < 0 && direction !== 'right' && checkDirection('left')) {
        direction = 'left';
    } else if (dy > 0 && direction !== 'up' && checkDirection('down')) {
        direction = 'down';
    } else if (dy < 0 && direction !== 'down' && checkDirection('up')) {
        direction = 'up';
    } else {
        const safeDirections = [];
        if (direction !== 'right' && checkDirection('left')) safeDirections.push('left');
        if (direction !== 'left' && checkDirection('right')) safeDirections.push('right');
        if (direction !== 'up' && checkDirection('down')) safeDirections.push('down');
        if (direction !== 'down' && checkDirection('up')) safeDirections.push('up');
        
        if (safeDirections.length > 0) {
            direction = safeDirections[Math.floor(Math.random() * safeDirections.length)];
        } else {
            direction = direction === 'right' ? 'up' : 'left';
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    snake.forEach((segment, index) => {
        ctx.fillStyle = index === 0 ? 'green' : 'lime';
        ctx.fillRect(segment.x * gridSize, segment.y * gridSize, gridSize, gridSize);
    });
    ctx.fillStyle = 'red';
    ctx.fillRect(food.x * gridSize, food.y * gridSize, gridSize, gridSize);
}

function move() {
    const head = {...snake[0]};
    switch (direction) {
        case 'up': head.y--; break;
        case 'down': head.y++; break;
        case 'left': head.x--; break;
        case 'right': head.x++; break;
    }

    if (head.x === food.x && head.y === food.y) {
        score++;
        food = {
            x: Math.floor(Math.random() * gridWidth),
            y: Math.floor(Math.random() * gridHeight)
        };
    } else {
        snake.pop();
    }

    if (head.x < 0 || head.x >= gridWidth || head.y < 0 || head.y >= gridHeight) {
        alert('游戏结束！得分: ' + score);
        resetGame();
        return;
    }

    for (let i = 0; i < snake.length; i++) {
        if (snake[i].x === head.x && snake[i].y === head.y) {
            alert('游戏结束！得分: ' + score);
            resetGame();
            return;
        }
    }

    snake.unshift(head);
}

function resetGame() {
    snake = [{x: 10, y: 10}];
    direction = 'right';
    score = 0;
    food = {
        x: Math.floor(Math.random() * gridWidth),
        y: Math.floor(Math.random() * gridHeight)
    };
}

function gameLoop() {
    calculateDirection();
    move();
    draw();
    setTimeout(gameLoop, 100);
}

gameLoop();