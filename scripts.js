document.addEventListener('DOMContentLoaded', function() {

    // If user is logged in
    if (document.querySelector("#username-link")) {
        document.getElementById('new-game-link').addEventListener('click', (event) => {
            new_game();
            event.preventDefault();
        });
        document.getElementById('my-games-link').addEventListener('click', (event) => {
            load_view('my-games', 1);
            event.preventDefault();
        });
    };
    // Initialize default board
    load_view('default', 0);
});

// Map chess piece on board_str to CSS class
const PIECE_MAP = {'r':'br', 'n':'bn', 'b':'bb', 'q':'bq', 'k':'bk', 'p':'bp', 'P':'wp', 'R':'wr', 'N':'wn', 'B':'wb', 'Q':'wq', 'K':'wk'}

function load_board(board_str, white_turn_bool, en_passant, b_castle, w_castle, bk_check, wk_check, winner) {
    document.getElementById('board_view').style.display = 'block';
    remove_event_listeners()
    for (let i = 0; i < 64; i++) {
        var square_letter = board_str.charAt(i);
        var square_id = 'square-'+i;
        piece = document.getElementById(square_id)
        // clear prev turn classes
        piece.className = ''
        piece.classList.add('col')

        if (square_letter != ' ') {
            // display chess pieces
            var image_class = PIECE_MAP[square_letter]
            piece.classList.add(image_class)
        }
    }
    mark_enemy_legal_moves(board_str, white_turn_bool, en_passant, b_castle, w_castle)
    // check endgame
    let wk = document.querySelector('.wk')
    let bk = document.querySelector('.bk')
    if (wk_check) {
        wk.classList.add('checked')
    }
    if (bk_check) {
        bk.classList.add('checked')
    }
    if (white_turn_bool) {
        if (wk_check) {
            // remove check
            if (!wk.classList.contains('enemy-attack')) {
                wk_check = false
                if (wk.classList.contains('checked')) {
                    wk.classList.remove('checked')
                }
            }
        } else {
            // set check
            if (wk.classList.contains('enemy-attack')) {
                wk_check = true
                wk.classList.add('checked')
            }
        }
        if (bk_check) {
            // checkmate
            let own_legal_moves = new Set()
            for (let i = 0; i < 64; i++) {
                if (board_str.charAt(i)!==" " && is_white(board_str, i)) {
                    let temp = legal_moves(board_str.charAt(i), i, board_str, en_passant, b_castle, w_castle)
                    for (var t of temp) {
                        own_legal_moves.add(t)
                    }
                }
            }
            for (var i of own_legal_moves) {
                if (board_str.charAt(i)==="k") {
                    winner = 'White'
                }
            }
        }
    } else { // black turn
        if (bk_check) {
            // remove check
            if (!bk.classList.contains('enemy-attack')) {
                bk_check = false
                if (bk.classList.contains('checked')) {
                    bk.classList.remove('checked')
                }
            }
        } else {
            // set check
            if (bk.classList.contains('enemy-attack')) {
                bk_check = true
                bk.classList.add('checked')
            }
        }
        if (wk_check) {
            // checkmate
            let own_legal_moves = new Set()
            for (let i = 0; i < 64; i++) {
                if (board_str.charAt(i)!==" " && is_black(board_str, i)) {
                    let temp = legal_moves(board_str.charAt(i), i, board_str, en_passant, b_castle, w_castle)
                    for (var t of temp) {
                        own_legal_moves.add(t)
                    }
                }
            }
            for (var i of own_legal_moves) {
                if (board_str.charAt(i)==="K") {
                    winner = 'Black'
                }
            }
        }
    }
    // remove previous winner alerts
    try {
        document.querySelectorAll('.alert').forEach(div => div.remove())
    } catch (error) {}
    // set legal moves
    if (winner===null) {
        for (let i = 0; i < 64; i++) {
            var square_letter = board_str.charAt(i);
            var square_id = 'square-'+i;
            piece = document.getElementById(square_id)
            if (square_letter != ' ') {
                if (white_turn_bool && is_white(board_str, i)) {
                    piece.addEventListener('click', (event) => {
                        mark_legal_moves(board_str.charAt(i), i, board_str, white_turn_bool, en_passant, b_castle, w_castle,  bk_check, wk_check, winner)
                        event.preventDefault();
                    })
                } else if (!white_turn_bool && is_black(board_str, i)) {
                    piece.addEventListener('click', (event) => {
                        mark_legal_moves(board_str.charAt(i), i, board_str, white_turn_bool, en_passant, b_castle, w_castle,  bk_check, wk_check, winner)
                        event.preventDefault();
                    })
                }
            }
        }
    } else { // alert winner
        //let Body = document.getElementById('board_view')
        let Body = document.querySelector('.col-lg-6')
        let winnerAlert = document.createElement('div')
        winnerAlert.classList.add('alert')
        winnerAlert.classList.add('alert-success')
        winnerAlert.innerHTML = `${winner} won`
        Body.appendChild(winnerAlert)
    }
};

function render_mini_board(boardString) {
    const boardSize = 8;
    const squareSize = 20;
    const board = document.createElement('canvas');
    board.width = boardSize * squareSize;
    board.height = boardSize * squareSize;
    const ctx = board.getContext('2d');
    for (let i = boardSize - 1; i >= 0; i--) {
      for (let j = boardSize - 1; j >= 0; j--) {
        const piece = boardString[i * boardSize + j];
        const isWhiteSquare = (i + j) % 2 === 0;
        ctx.fillStyle = isWhiteSquare ? '#ffce9e' : '#d18b47';
        ctx.fillRect(j * squareSize, (boardSize - i - 1) * squareSize, squareSize, squareSize);
        if (piece !== ' ') {
          const img = new Image();
          img.onload = function() {
            ctx.drawImage(img, j * squareSize, (boardSize - i - 1) * squareSize, squareSize, squareSize);
          };
          img.src = `static/board/assets/${PIECE_MAP[piece]}.svg`;
        }
      }
    }
    return board;
  }

function mark_legal_moves(piece_str, square_int, board_str, white_turn_bool, en_passant, b_castle, w_castle,  bk_check, wk_check, winner) {
    // remove prev marked moves
    if (document.getElementsByClassName('blue-circle').length>0 || document.getElementsByClassName('green-circle').length>0) {
        load_board(board_str, white_turn_bool, en_passant, b_castle, w_castle,  bk_check, wk_check, winner)
    }
    var legalMoves = legal_moves(piece_str, square_int, board_str, en_passant, b_castle, w_castle)
    for (let i of legalMoves) {
        var square_id = 'square-'+i
        tile = document.getElementById(square_id)
        if (is_empty(board_str, i)) {
            tile.classList.add('blue-circle')
        } else {tile.classList.add('green-circle')}
        tile.addEventListener('click', (event) => {
            make_move(piece_str, square_int, board_str, i, white_turn_bool, en_passant, b_castle, w_castle, bk_check, wk_check, winner)
            event.preventDefault();
        })
    }
};

function mark_enemy_legal_moves(board_str, white_turn_bool, en_passant, b_castle, w_castle) {
    var enemy_legal_moves = new Set()
    if (white_turn_bool) {
        // mark black legal moves
        for (let i = 0; i < 64; i++) {
            if (is_black(board_str, i)) {
                if(board_str.charAt(i)==='p') {
                    var pawn_attacks = legal_pawn_attacks(board_str, i)
                    for (var p of pawn_attacks) {
                        enemy_legal_moves.add(p)
                    }
                } else {
                    let piece_legal_moves = legal_moves(board_str.charAt(i), i, board_str, en_passant, b_castle, w_castle)
                    for (var l of piece_legal_moves) {
                        enemy_legal_moves.add(l)
                        // checkmate path
                    }
                }
            }
        }
    } else {
        // mark white legal moves
        for (let i = 0; i < 64; i++) {
            if (is_white(board_str, i)) {
                if(board_str.charAt(i)==='P') {
                    var  pawn_attacks = legal_pawn_attacks(board_str, i)
                    for (var p of pawn_attacks) {
                        enemy_legal_moves.add(p)
                    }
                } else {
                    let piece_legal_moves = legal_moves(board_str.charAt(i), i, board_str, en_passant, b_castle, w_castle)
                    for (var l of piece_legal_moves) {
                        enemy_legal_moves.add(l)
                        // checkmate path
                    }
                }
            }
        }
    }
    for (var i of enemy_legal_moves) {
        var square_id = 'square-'+i;
        square = document.getElementById(square_id)
        square.classList.add('enemy-attack')
    }
}

function new_game() {
    fetch('new', {
      method: 'POST',
      body: JSON.stringify({
          board_str: "RNBQKBNRPPPPPPPP                                pppppppprnbqkbnr" // TEST
        })
      })
    .then(response => response.json())
    .then(game => load_match(game.id))
    }

function list_matches(page) {
    // Pagination vars
    let prev_page = page - 1;
    let next_page = page + 1;

    const myGamesView = document.getElementById('my_games_view')
    myGamesView.style.display = 'block';
    const myGamesList = document.getElementById('my_games_list')

    fetch(`list/${page}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(matches => {
        let prev_page_exists = matches.slice(-2,-1)[0]["prev"];
        let next_page_exists = matches.slice(-1)[0]["next"];
        // Render at most 10 matches
        matches.slice(0,-2).forEach(match => {
            const div = document.createElement('div');
            div.className = "match_div";
            div.id = `match${match.id}`;
            let miniBoard =  render_mini_board(match.board);
            miniBoard.className = "mini_board";
            div.appendChild(miniBoard);
            miniBoard.addEventListener('click', (event) => {
                load_match(`${match.id}`);
                const myGamesView = document.getElementById('my_games_view')
                myGamesView.style.display = 'none';
                event.preventDefault();
            })
            const miniInfo = document.createElement('div');
            miniInfo.className = "mini_info"
            miniInfo.innerHTML = match.w_turn ? "<p>White player's turn</p>" : "<p>Black player's turn</p>";
            miniInfo.innerHTML += `<p>created ${match.timestamp}</p>`
            miniInfo.innerHTML += match.winner===null ? "" : `<p>${match.winner} won</p>` // Error all matches list winner as null
            div.appendChild(miniInfo);
            myGamesList.appendChild(div);
        });
        // Set pagination links
        const prev_link = document.querySelector('#prev-page');
        if (prev_page_exists) {
            prev_link.parentElement.className = "page-item";
            prev_link.addEventListener('click', prev_page_link = (event) => {
            load_view("my-games", prev_page);
            event.preventDefault();
            }, { once: true });
        } else {
            prev_link.parentElement.className = "page-item disabled";
        }
        const next_link = document.querySelector('#next-page');
        if (next_page_exists) {
            next_link.parentElement.className = "page-item";
            
            next_link.addEventListener('click', next_page_link = (event) => {
            load_view("my-games", next_page);
            event.preventDefault();
            }, { once: true });
        } else {
            next_link.parentElement.className = "page-item disabled";
        }
    });
}

function load_match(match_id) {
    fetch(`match/${match_id}`)
    .then(response => response.json())
    .then(match  => {
        load_board(match.board, match.w_turn, match.en_passant, match.b_castle, match.w_castle, match.bk_check, match.wk_check, match.winner);
        document.getElementById('match-id').innerHTML = match_id
    })
}

function make_move(piece_str, square_int, board_str, move_int, white_turn_bool, en_passant, b_castle, w_castle,  bk_check, wk_check, winner) {

    var en_passant_attack = -1;
    if (en_passant!=="") {
        if (move_int===parseInt(en_passant.slice(2,4))) {
            if (is_white(board_str, square_int)) {
                en_passant_attack = move_int-8
            } else {en_passant_attack = move_int+8}
        }
        if (move_int===parseInt(en_passant.slice(6,8))) {
            if (is_white(board_str, square_int)) {
                en_passant_attack = move_int-8
            } else {en_passant_attack = move_int+8}
        }
    }
    en_passant = ""
    if (piece_str==='p') {
        // Set en passant
        if (square_int - move_int===16) {
            if (!leftBorder.has(move_int)) {
                if (board_str.charAt(move_int-1)==='P') {
                    en_passant +=  move_int-1
                    en_passant +=   square_int-8
                }
            }
            if (!rightBorder.has(move_int)) {
                if (board_str.charAt(move_int+1)==='P') {
                    en_passant +=  move_int+1
                    en_passant +=  square_int-8
                }
            }
            // promotion TODO allow choices
        } else if (bottomBorder.has(move_int)) {
            piece_str = "q"
        }
    }
    if (piece_str==='P') {
        // Set en passant
        if (square_int - move_int===-16) {
            if (!leftBorder.has(move_int)) {
                if (board_str.charAt(move_int-1)==='p') {
                    en_passant +=  move_int-1
                    en_passant +=   square_int+8
                }
            }
            if (!rightBorder.has(move_int)) {
                if (board_str.charAt(move_int+1)==='p') {
                    en_passant +=  move_int+1
                    en_passant +=   square_int+8
                }
            }
            // promotion TODO allow choices
        } else if (topBorder.has(move_int)) {
            piece_str = "Q"
        }
    }
    if (piece_str==='r') {
        if  (b_castle!=="n") {
            if (square_int===56) {
                if (b_castle==="l") {
                    b_castle = "n"
                } else {
                    b_castle = "r"
                }
            } else if (square_int===63) {
                if (b_castle==="r") {
                    b_castle = "n"
                } else {
                    b_castle = "l"
                }
            }
        }
    }
    if (piece_str==='R') {
        if  (w_castle!=="n") {
            if (square_int===0) {
                if (w_castle==="l") {
                    w_castle = "n"
                } else {
                    w_castle = "r"
                }
            } else if (square_int===7) {
                if (w_castle==="r") {
                    w_castle = "n"
                } else {
                    w_castle = "l"
                }
            }
        }
    }
    if (is_castle_move(piece_str, square_int, move_int)) {
        is_left_move = square_int-move_int > 0
        if (is_left_move) {
            rook_int = square_int-4
            rook_str = board_str.charAt(rook_int)
            rmRook = board_str.slice(0,rook_int)+' '+board_str.slice(rook_int+1,64);
            addRook = rmRook.slice(0,move_int+1)+rook_str+ rmRook.slice(move_int+2,64);
        } else {
            rook_int = square_int+3
            rook_str = board_str.charAt(rook_int)
            rmRook = board_str.slice(0,rook_int)+' '+board_str.slice(rook_int+1,64);
            addRook = rmRook.slice(0,move_int-1)+rook_str+ rmRook.slice(move_int,64);
        }
        tempBoardStr = addRook.slice(0,square_int)+' '+addRook.slice(square_int+1,64);
        if (is_black(board_str, square_int)) {
            b_castle = "n"
        } else {
            w_castle = "n"
        }
    } else if (en_passant_attack!==-1) {
        rmAttacked = board_str.slice(0,en_passant_attack)+' '+board_str.slice(en_passant_attack+1,64);
        tempBoardStr = rmAttacked.slice(0,square_int)+' '+rmAttacked.slice(square_int+1,64);
    } else {
        tempBoardStr = board_str.slice(0,square_int)+' '+board_str.slice(square_int+1,64);
    }
    resBoardStr = tempBoardStr.slice(0, move_int)+piece_str+tempBoardStr.slice(move_int+1,64)
    match_id = document.getElementById('match-id').innerHTML
    if (match_id==='') {
        load_board(resBoardStr, !white_turn_bool, en_passant, b_castle, w_castle, bk_check, wk_check, winner);
    } else {
        fetch(`move/${match_id}`, {
            method: 'PUT',
            body: JSON.stringify({
                board_str: resBoardStr,
                en_passant: en_passant,
                w_turn: !white_turn_bool,
                w_castle: w_castle,
                b_castle: b_castle,
                wk_check: wk_check,
                bk_check: bk_check,
                winner: winner
                // add en_passant, castling, check, promotion
            })
        })
        .then(response => {
            if (response.ok) {
                load_board(resBoardStr, !white_turn_bool, en_passant, b_castle, w_castle, bk_check, wk_check, winner)
            }
        })
    }
}

function load_view(view, page) {
    // hide all views, they will be displayed by their corresponding functions
    document.getElementById('board_view').style.display = 'none';
    document.getElementById('my_games_view').style.display = 'none';

    if (view === 'default') {
        load_board("RNBQKBNRPPPPPPPP                                pppppppprnbqkbnr", true, "", "b", "b", false, false, null);
    }
    else if (view === 'my-games') {
        // clear links to prev rendered matches if any
        try {
            document.querySelectorAll('div.match_div').forEach(div => div.remove())
        } catch (error) {}
        // clear prev paginaton links
        try {
            document.querySelector('#prev-page').removeEventListener('click', prev_page_link);
          } catch {}
          try {
            document.querySelector('#next-page').removeEventListener('click', next_page_link);
          } catch {}
        list_matches(page)
    }
}

/* Helpers */
function is_empty(board_str, square_int) {
    return board_str.charAt(square_int) == ' ';
};
// beware is_color() returns true on ' '
function is_black(board_str, square_int) {
    return board_str.charAt(square_int)===board_str.charAt(square_int).toLowerCase();
};
function is_white(board_str,square_int) {
    return board_str.charAt(square_int)===board_str.charAt(square_int).toUpperCase();
};
function range(start, end, step = 1) {
    const length = Math.ceil((end - start) / step);
    return Array.from({ length }, (_, i) => start + i * step);
};
function remove_event_listeners() {
    var background = document.getElementById('board-background')
    var clone = background.cloneNode(true)
    background.parentNode.replaceChild(clone, background)
};
function is_castle_move(piece_str, square_int, move_int) {
    return ((piece_str==="K" || piece_str==="k") && (Math.abs(square_int-move_int)===2))
}
function legal_pawn_attacks(board_str, square_int) {
    var res = []
    if (board_str.charAt(square_int)==="P") {
        if (!leftBorder.has(square_int)) {
            res.push(square_int+7)
        }
        if (!rightBorder.has(square_int)) {
            res.push(square_int+9)
        }
    } if (board_str.charAt(square_int)==="p") {
        if (!leftBorder.has(square_int)) {
            res.push(square_int-9)
        }
        if (!rightBorder.has(square_int)) {
            res.push(square_int-7)
        }
    }
    return res
}

// Positional helpers
const leftBorder = new Set(range(0,64,8))
const rightBorder = new Set(range(7,64,8))
const topBorder = new Set(range(56,64,1))
const bottomBorder = new Set(range(0,8,1))
const whitePawnDoubleMove = new Set(range(8,16,1))
const blackPawnDoubleMove = new Set(range(48,56,1))

function legal_moves(piece_str, square_int, board_str, en_passant, b_castle, w_castle) {
    /* Return array of squares (int 0 - 63) that are valid destinations */
    var legalMoves = []
    /* Pawn */
    if (en_passant!=="") {
        if (square_int===parseInt(en_passant.slice(0,2))) {
            legalMoves.push(parseInt(en_passant.slice(2,4)));
        }
        if (square_int===parseInt(en_passant.slice(4,6))) { // slice output "" on > length parseInt output NaN on ""
            legalMoves.push(parseInt(en_passant.slice(6,8)));
        }
    }
    if (piece_str=='p') {
        /* black pawn not in lowermost rank */
        if (!bottomBorder.has(square_int)) {
            /* forward move not blocked */
            if(is_empty(board_str, square_int-8)) {
                legalMoves.push(square_int-8);
                /* move 2 squares */
                if (blackPawnDoubleMove.has(square_int)) {
                    if (is_empty(board_str, square_int-16)) {
                        legalMoves.push(square_int-16);
                    }
                }
            }
            /* available attack targets */
            if (square_int%8==0) {
                if (!is_empty(board_str, square_int-7) && is_white(board_str, square_int-7)) {
                    legalMoves.push(square_int-7);
                }
            } else if (square_int%8==7) {
                if (!is_empty(board_str, square_int-9) && is_white(board_str, square_int-9)) {
                    legalMoves.push(square_int-9);
                }
            } else {
                if (!is_empty(board_str, square_int-7) && is_white(board_str, square_int-7)) {
                    legalMoves.push(square_int-7);
                }
                if (!is_empty(board_str, square_int-9) && is_white(board_str, square_int-9)) {
                    legalMoves.push(square_int-9);
                }
            }
        }
    }
    else if (piece_str=='P') {
        /* white pawn not at the uppermost rank */
        if (!topBorder.has(square_int)) {
            /* forward move not blocked */
            if(board_str.charAt(square_int+8) == ' ') {
                legalMoves.push(square_int+8);
                /* move 2 squares */
                if (whitePawnDoubleMove.has(square_int)) {
                    if (is_empty(board_str, square_int+16)) {
                        legalMoves.push(square_int+16)
                    }
                }
            }
            /* available diagonal attack targets */
            if (square_int%8==0) {
                if (!is_empty(board_str,square_int+9) && is_black(board_str,square_int+9)) {
                    legalMoves.push(square_int+9)
                }
            } else if (square_int%8==7) {
                if (!is_empty(board_str,square_int+7) && is_black(board_str,square_int+7)) {
                    legalMoves.push(square_int+7)
                }
            } else {
                if (!is_empty(board_str,square_int+7) && is_black(board_str,square_int+7)) {
                    legalMoves.push(square_int+7)
                }
                if (!is_empty(board_str,square_int+9) && is_black(board_str,square_int+9)) {
                    legalMoves.push(square_int+9)
                }
            }
        }
    }
    /* Rook */
    else if (piece_str=='r' || piece_str=='R') {
        /* up */
        for (var i of range(square_int+8, 64, 8)) {
            if (is_empty(board_str,i)) {
                legalMoves.push(i)
            } else if (piece_str=='r') { 
                if (is_white(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break} 
            } else if (piece_str=='R') { 
                if (is_black(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break}
            }
        }
        /* down */
        for (var i of range(square_int-8,-1,-8)) {
            if (is_empty(board_str,i)) {
                legalMoves.push(i)
            } else if (piece_str=='r') { 
                if (is_white(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break} 
            } else if (piece_str=='R') { 
                if (is_black(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break}
            }
        }
        /* left */
        for (var i of range(square_int-1, (Math.floor(square_int/8)*8)-1,-1)) {
            if (is_empty(board_str,i)) {
                legalMoves.push(i)
            } else if (piece_str=='r') { 
                if (is_white(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break} 
            } else if (piece_str=='R') { 
                if (is_black(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break}
            }
        }
        /* right */
        for (var i of range(square_int+1, ((Math.floor(square_int/8)+1)*8),1)) {
            if (is_empty(board_str,i)) {
                legalMoves.push(i)
            } else if (piece_str=='r') { 
                if (is_white(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break} 
            } else if (piece_str=='R') { 
                if (is_black(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break}
            }
        }
    }
    /* Knight */
    else if (piece_str=='n'  || piece_str=='N') {
        var checkMoves = []
        up2left1 = square_int+15
        up2right1 = square_int+17
        for (var i of [up2left1, up2right1]) {
            if (i<64 && Math.floor(i/8) == Math.floor(square_int/8)+2) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i);
                } else if (piece_str=='n') {
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                    }
                } else if (piece_str=='N') {
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                    }
                }
            }
        }
        down2left1 = square_int-17
        down2right1 = square_int-15
        for (var i of [down2left1, down2right1]) {
            if (i>=0 && Math.floor(i/8) == Math.floor(square_int/8)-2) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i);
                } else if (piece_str=='n') {
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                    }
                } else if (piece_str=='N') {
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                    }
                }
            }
        }
        up1left2 = square_int+6
        up1right2 = square_int+10
        for (var i of [up1left2, up1right2]) {
            if (i<64 && Math.floor(i/8) == Math.floor(square_int/8)+1) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i);
                } else if (piece_str=='n') {
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                    }
                } else if (piece_str=='N') {
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                    }
                }
            }
        }
        down1left2 = square_int-10
        down1right2 = square_int-6
        for (var i of [down1left2, down1right2]) {
            if (i>=0 && Math.floor(i/8) == Math.floor(square_int/8)-1) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i);
                } else if (piece_str=='n') {
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                    }
                } else if (piece_str=='N') {
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                    }
                }
            }
        }
    }
    /* Bishop */
    else if (piece_str=='b' || piece_str=='B') {
        /* top left */
        if (!topBorder.has(square_int) && !leftBorder.has(square_int)) {
            for (var i of range(square_int+7, 64, 7)) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i)
                } else if (piece_str=='b') { 
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break} 
                } else if (piece_str=='B') { 
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break}
                }
                if (topBorder.has(i) || leftBorder.has(i)) {
                    break
                }
            }
        }
        /* top right */
        if (!topBorder.has(square_int) && !rightBorder.has(square_int)) {
            for (var i of range(square_int+9, 64, 9)) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i)
                } else if (piece_str=='b') { 
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break} 
                } else if (piece_str=='B') { 
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break}
                }
                if (topBorder.has(i) || rightBorder.has(i)) {
                    break
                }
            }
        }
        /* bottom left */
        if (!bottomBorder.has(square_int) && !leftBorder.has(square_int)) {
            for (var i of range(square_int-9, -1, -9)) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i)
                } else if (piece_str=='b') { 
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break} 
                } else if (piece_str=='B') { 
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break}
                }
                if (bottomBorder.has(i) || leftBorder.has(i)) {
                    break
                }
            }
        }
        /* bottom right */
        if (!bottomBorder.has(square_int) && !rightBorder.has(square_int)) {
            for (var i of range(square_int-7, -1, -7)) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i)
                } else if (piece_str=='b') { 
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break} 
                } else if (piece_str=='B') { 
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break}
                }
                if (bottomBorder.has(i) || rightBorder.has(i)) {
                    break
                }
            }
        }
    }
    /* King */
    else if (piece_str=='k' || piece_str=='K') {
        const checkMoves = new Set()
        const legalMoves = []
        if (!topBorder.has(square_int)) {
            checkMoves.add(square_int+8);
            if (!leftBorder.has(square_int)) {
                checkMoves.add(square_int+7);
                checkMoves.add(square_int-1);
            }
            if (!rightBorder.has(square_int)) {
                checkMoves.add(square_int+9);
                checkMoves.add(square_int+1);
            }
        }
        if (!bottomBorder.has(square_int)) {
            checkMoves.add(square_int-8);
            if (!leftBorder.has(square_int)) {
                checkMoves.add(square_int-9);
                checkMoves.add(square_int-1);
            }
            if (!rightBorder.has(square_int)) {
                checkMoves.add(square_int-7);
                checkMoves.add(square_int+1);
            }
        }
        for (var i of checkMoves) {
            var square_id = 'square-'+i;
            square = document.getElementById(square_id)
            if (!square.classList.contains('enemy-attack')) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i)
                } else if (piece_str=='k') {
                    if (is_white(board_str, i)) {
                    legalMoves.push(i)
                    }
                } else if (piece_str=='K') {
                    if (is_black(board_str, i)) {
                    legalMoves.push(i)
                    }
                }
            }
        }
        if (piece_str==="k") {
            if (b_castle!=="n") {
                if (b_castle==="l" || b_castle==="b") {
                    
                    if (is_empty(board_str, square_int-1) && is_empty(board_str, square_int-2) && is_empty(board_str, square_int-3)) {
                        let a = square_int-1
                        let b = square_int-2
                        let c = square_int-3
                        if (!document.getElementById('square-'+a).classList.contains('enemy-attack') && !document.getElementById('square-'+b).classList.contains('enemy-attack') && !document.getElementById('square-'+c).classList.contains('enemy-attack')) {
                            legalMoves.push(square_int-2)
                        }
                    }
                }
                if (b_castle==="r" || b_castle==="b") {
                    if (is_empty(board_str, square_int+1) && is_empty(board_str, square_int+2)) {
                        let d = square_int+1
                        let e = square_int+2
                        if (!document.getElementById('square-'+d).classList.contains('enemy-attack') && !document.getElementById('square-'+e).classList.contains('enemy-attack')) {
                            legalMoves.push(square_int+2)
                        }
                    }
                }
            }
        } else if (piece_str==="K") {
            if (w_castle!=="n") {
                if (w_castle==="l" || w_castle==="b") {
                    if (is_empty(board_str, square_int-1) && is_empty(board_str, square_int-2) && is_empty(board_str, square_int-3)) {
                        let a = square_int-1
                        let b = square_int-2
                        let c = square_int-3
                        if (!document.getElementById('square-'+a).classList.contains('enemy-attack') && !document.getElementById('square-'+b).classList.contains('enemy-attack') && !document.getElementById('square-'+c).classList.contains('enemy-attack')) {
                            legalMoves.push(square_int-2)
                        }
                    }
                }
                if (w_castle==="r" || w_castle==="b") {
                    if (is_empty(board_str, square_int+1) && is_empty(board_str, square_int+2)) {
                        let d = square_int+1
                        let e = square_int+2
                        if (!document.getElementById('square-'+d).classList.contains('enemy-attack') && !document.getElementById('square-'+e).classList.contains('enemy-attack')) {
                            legalMoves.push(square_int+2)
                        }
                    }
                }
            }
        }
        return legalMoves
    }
    /* Queen */
    else if (piece_str=='q' || piece_str=='Q') {
        /* top left */
        if (!topBorder.has(square_int) && !leftBorder.has(square_int)) {
            for (var i of range(square_int+7, 64, 7)) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i)
                } else if (piece_str=='q') { 
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break} 
                } else if (piece_str=='Q') { 
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break}
                }
                if (topBorder.has(i) || leftBorder.has(i)) {
                    break
                }
            }
        }
        /* top right */
        if (!topBorder.has(square_int) && !rightBorder.has(square_int)) {
            for (var i of range(square_int+9, 64, 9)) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i)
                } else if (piece_str=='q') { 
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break} 
                } else if (piece_str=='Q') { 
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break}
                }
                if (topBorder.has(i) || rightBorder.has(i)) {
                    break
                }
            }
        }
        /* bottom left */
        if (!bottomBorder.has(square_int) && !leftBorder.has(square_int)) {
            for (var i of range(square_int-9, -1, -9)) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i)
                } else if (piece_str=='q') { 
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break} 
                } else if (piece_str=='Q') { 
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break}
                }
                if (bottomBorder.has(i) || leftBorder.has(i)) {
                    break
                }
            }
        }
        /* bottom right */
        if (!bottomBorder.has(square_int) && !rightBorder.has(square_int)) {
            for (var i of range(square_int-7, -1, -7)) {
                if (is_empty(board_str, i)) {
                    legalMoves.push(i)
                } else if (piece_str=='q') { 
                    if (is_white(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break} 
                } else if (piece_str=='Q') { 
                    if (is_black(board_str, i)) {
                        legalMoves.push(i)
                        break
                    } else {break}
                }
                if (bottomBorder.has(i) || rightBorder.has(i)) {
                    break
                }
            }
        }
        /* up */
        for (var i of range(square_int+8, 64, 8)) {
            if (is_empty(board_str,i)) {
                legalMoves.push(i)
            } else if (piece_str=='q') { 
                if (is_white(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break} 
            } else if (piece_str=='Q') { 
                if (is_black(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break}
            }
        }
        /* down */
        for (var i of range(square_int-8,-1,-8)) {
            if (is_empty(board_str,i)) {
                legalMoves.push(i)
            } else if (piece_str=='q') { 
                if (is_white(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break} 
            } else if (piece_str=='Q') { 
                if (is_black(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break}
            }
        }
        /* left */
        for (var i of range(square_int-1, (Math.floor(square_int/8)*8)-1,-1)) {
            if (is_empty(board_str,i)) {
                legalMoves.push(i)
            } else if (piece_str=='q') { 
                if (is_white(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break} 
            } else if (piece_str=='Q') { 
                if (is_black(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break}
            }
        }
        /* right */
        for (var i of range(square_int+1, ((Math.floor(square_int/8)+1)*8),1)) {
            if (is_empty(board_str,i)) {
                legalMoves.push(i)
            } else if (piece_str=='q') { 
                if (is_white(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break} 
            } else if (piece_str=='Q') { 
                if (is_black(board_str, i)) {
                    legalMoves.push(i)
                    break
                } else {break}
            }
        }
    }
    return legalMoves;
};