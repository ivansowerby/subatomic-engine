$(document).ready(() => {
    /** @type {HTMLCanvasElement} */
    const canvas = $("#snake-game-canvas");
    const canvasDOM = canvas.get(0);
    const ctx = canvasDOM.getContext("2d");

    //resize
    ctx.canvas.width = canvas.width();
    ctx.canvas.height = canvas.height();
 
    //snake
    window.begin = () => {
        if(window.interval !== undefined || typeof window.interval !== "undefined") { clearInterval(interval) }
        parseJSON("json", "canvas.json").then((object) => {
            window.canvas = object;
            const canvas = window.canvas["name"]["snake-game-canvas"];
            window.width = canvas["width"];
            window.height = Math.round(width * ctx.canvas.height / ctx.canvas.width);
            eel.snakeBegin(window.width, window.height)(() => {
                $("body").on("keydown", (e) => {
                    if(!$("input[type=text]").is(":focus")) {
                        const key = translateKey(e);
                        $(`#${key}-arrow-button`).trigger("click");
                    }
                });
                parseJSON("json", "attributes.json").then((object) => {
                    window.attributes = object;
                    render();
                    initiateInterval(update, 100);
                });
            });
        });
    }

    window.begin()

    const update = () => {
        eel.snakeUpdate(window.username)(() => {
            eel.snakeIsGameOver()((gameOver) => {
                if(gameOver) { 
                    clearInterval(window.interval); }
                else {
                    editCurrentScore();
                    editHighScore();
                    render();
                }
            });
        });
    }

    const render = () => {
        Promise.all([
            eel.getObjects()(),
            eel.getAttributes()()
        ]).then(([_objects, _attributes]) => {
            let layers = {}
            for(const [uid, props] of Object.entries(_objects)) {
                const gid = props["gid"];
                let name = props["name"];
                const body = props["body"];
                const velocity = props["velocity"];

                let number = 0
                if(name.includes('-')) {
                    const i = name.lastIndexOf('-');
                    number = parseInt(name.slice(i + 1));
                    name = name.slice(0, i);
                }
                
                const attributes = Object.assign({}, window.attributes["name"][name], _attributes[gid]);
                if(name != attributes["name"]) { continue; }
                const colour = attributes["colour"];
                const priorityLevel = attributes["priority-level"];

                const layer = {
                    [uid]: {
                        "name": name,
                        "colour": colour,
                        "body": body
                    }
                };
                layers[priorityLevel] = Object.assign({}, layers[priorityLevel], layer); 
            }
            clear()
            for(const priorityLevel of Object.keys(layers).sort()) {
                const layer = layers[priorityLevel];
                for(const [uid, values] of Object.entries(layer)) {
                    const name = values["name"];
                    const colour = values["colour"];
                    const body = values["body"];
                    for(const coordinates of body) {
                        draw(coordinates, colour);
                    }
                }
            }
            const grid = window.attributes["name"]["grid"];
            const colour = grid["colour"];
            drawGrid(colour);
        });
    }

    $("#submit-button").on("click", () => {
        //validation & sanitisation
        const usernameInput = $("#username-input[type=text]");
        window.username = usernameInput.val()
            .replace(" ", "")
            .toLowerCase();
        usernameInput.val(window.username);
        editHighScore();
    });

    const editCurrentScore = () => {
        eel.snakeLength()((length) => $("#current-score").children().eq(0).text(length));
    }

    const editHighScore = () => {
        eel.getUserHighScore(window.username)((highScore) => {
            $("#high-score").children().eq(0).text(highScore);
        });
    }

    const draw = (coordinates, colour) => {
        const [y, x] = coordinates;
        const dy = ctx.canvas.width / window.width;
        const dx = ctx.canvas.height / window.height;
        ctx.fillStyle = colour;
        ctx.fillRect(x * dx, y * dy, dx, dy);
    }

    const drawGrid = (colour) => {
        const dy = ctx.canvas.height / window.height;
        const dx = ctx.canvas.width / window.width;
        ctx.strokeStyle = colour;
        for(let i = 1; i < window.width; i++) {
            const x = dx * i;
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, ctx.canvas.height);
            ctx.stroke();
        }
        for(let j = 1; j < window.height; j++) {
            const y = dy * j;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(ctx.canvas.width, y);
            ctx.stroke();
        }
    }

    const clear = () => {
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    }
});

const parseJSON = (...filepath) => {
    return new Promise((resolve, reject) => {
      eel.pathConjoin(...filepath)((_url) => {
        $.getJSON(_url)
          .done((object) => resolve(object))
          .fail((error) => reject(error));
      });
    });
  };

const translateKey = (e) => {
    const key = e.key.toLowerCase();
    if(key.includes("arrow")) {  
        e.preventDefault();
        return key.replace("arrow", "");
    }
    else if(key == "w") { return "up"; }
    else if(key == "a") { return "left"; }
    else if(key == "s") { return "down"; }
    else if(key == "d") { return "right"; }
    return ""
}

const initiateInterval = (callback, timeout) => {
    callback();
    window.interval = setInterval(callback, timeout);
}