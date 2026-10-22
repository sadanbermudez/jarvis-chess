# Commentary and extracted claims

Check that every claim below appears in the commentary above it, and that the commentary makes no checkable statement missing from the list.

## grounded · https://lichess.org/ZRLfDc2e · ply 28 · Black played Nxd5, engine best Nfd7

FEN before: `r1b1k2r/1pq1bp2/2pp1npp/p1nPp3/P1B1P2N/BPN4P/2P2PP1/R2QR1K1 b kq - 2 14`

> By playing 14...Nxd5, Black blundered, allowing White to seize a decisive +3.75 advantage instead of the +1.29 White held after the engine-preferred 14...Nfd7. The immediate tactical flaw is that the pawn on e5 was hanging and pinned, as confirmed by the pre-move facts showing it attacked by a cheaper piece and its status as a hanging piece. In the resulting position after 14...Nxd5 15. exd5, Black’s e5-pawn is no longer defended, creating a direct material weakness that White exploits. The engine line 14...Nfd7 maintains a manageable +0.56 evaluation by keeping the position solid and avoiding this structural collapse.

- TRUE: `{"type": "best_move", "move": "Nfd7", "position": "before"}` (engine top 2: ['Nfd7', 'Na6'])
- FALSE: `{"type": "hanging", "square": "e5", "position": "before"}` (computed from attackers and defenders)
- FALSE: `{"type": "attacked_by_cheaper", "square": "e5", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "advantage", "side": "white", "position": "before"}` (engine +1.32 for White)
- to label by hand: After 14...Nxd5, the evaluation jumps to +3.75 for White.
- to label by hand: The engine line 14...Nfd7 leads to an evaluation of +1.29.
- to label by hand: The pawn on e5 is pinned.
- to label by hand: The pawn on e5 is attacked by a cheaper piece.

## grounded · https://lichess.org/ZRLfDc2e · ply 34 · Black played Qd7, engine best Qd8

FEN before: `r1b1k2r/1pq2p2/2pP2pp/p1p1p3/P1B4b/1PN4P/2P2PP1/R2QR1K1 b kq - 0 17`

> At move 17..., `Qd7` is a mistake that allows White to capture the hanging pawn on e5 with check, as the queen on d7 fails to defend it. The engine’s preferred move `Qd8` maintains the defense of the e5 pawn, preventing the immediate tactical blow `18. Rxe5+`. By failing to protect the pinned e5 pawn and the hanging queen on c7, `Qd7` drops a significant amount of evaluation from +4.17 to +7.01.

- TRUE: `{"type": "hanging", "square": "e5", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "hanging", "square": "c7", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "pinned", "square": "e5", "position": "before"}` (pinned to its own king)
- TRUE: `{"type": "best_move", "move": "Qd8", "position": "before"}` (engine top 2: ['Qd8', 'Qb6'])
- TRUE: `{"type": "advantage", "side": "white", "position": "before"}` (engine +5.10 for White)
- to label by hand: The move 17... Qd7 fails to defend the e5 pawn, allowing 18. Rxe5+.
- to label by hand: The move 17... Qd8 defends the e5 pawn and prevents the check on e5.
- to label by hand: The e5 pawn was pinned before 17... Qd7.

## grounded · https://lichess.org/BcAhQn3U · ply 33 · White played Ba1, engine best Ne5

FEN before: `2rqr1k1/p4ppp/1pn2bb1/2pp4/3Pn1P1/1P2PN1P/PB1N1PB1/2RQR1K1 w - - 1 17`

> By playing 17. Ba1, White abandoned the strong central outpost on e5, allowing Black to consolidate with 17... Bxe5 18. dxe5 Qh4. The engine’s preferred 17. Ne5 would have maintained dynamic tension and kept the evaluation near neutral, whereas the actual move caused a drastic drop to -3.25. This blunder effectively ceded the initiative and allowed Black to activate the queen aggressively. The subsequent sequence highlights how White's passive bishop placement contributed to the collapse of the kingside defense.

- TRUE: `{"type": "best_move", "move": "Ne5", "position": "before", "position_defaulted": true}` (engine top 2: ['Ne5', 'a3'])
- to label by hand: The move 17. Ba1 is graded as a blunder with an evaluation drop from -0.56 to -3.25.
- to label by hand: 17. Ne5 allows the continuation 17... Bxe5 18. dxe5 Qh4 19. Rf1 Ng5.
- to label by hand: White's evaluation after 17. Ba1 is -3.25.

## grounded · https://lichess.org/BcAhQn3U · ply 60 · Black played Bf3, engine best Rf8

FEN before: `2r1r1k1/p2R2p1/1p6/2p1p2b/4p2q/1P2P3/P2Q1PB1/1R3K2 b - - 1 30`

> At ply 60, Black’s `Bf3` is a blunder that squanders a winning advantage, dropping the evaluation from -5.16 to -1.21. The engine identifies `Rf8` as the best move, maintaining the pressure and leading to a decisive advantage (-5.16). `Bf3` allows White to simplify via `Qd5+`, whereas `Rf8` keeps the initiative and restricts White’s counterplay.

- TRUE: `{"type": "best_move", "move": "Rf8", "position": "before"}` (engine top 2: ['Rf8', 'Kh8'])
- TRUE: `{"type": "advantage", "side": "black", "position": "before"}` (engine -5.69 for White)
- to label by hand: Black played Bf3 which is graded as a blunder.
- to label by hand: The best move for Black at this position is Rf8.
- to label by hand: After Bf3, the evaluation improves for White to -1.21.
- to label by hand: After Rf8, the evaluation remains -5.16 in Black's favor.
- to label by hand: Bf3 allows White to play Qd5+ to complicate the position.

## grounded · https://lichess.org/BcAhQn3U · ply 63 · White played Qf7, engine best Bxf3

FEN before: `2r1r2k/p2R2p1/1p6/2pQp3/4p2q/1P2Pb2/P4PB1/1R3K2 w - - 4 32`

> 17. Ba1 is a blunder that drops the evaluation from -0.56 to -3.25 by ignoring the strong centralizing move 17. Ne5. The engine's best move 17. Ne5 forces 17... Bxe5 18. dxe5 Qh4 19. Rf1 Ng5, maintaining a manageable disadvantage. In contrast, 17. Ba1 allows Black to consolidate their advantage with no immediate compensation for White.

- FALSE: `{"type": "best_move", "move": "Ne5", "position": "before"}` (engine top 2: ['Bxf3', 'Qb7'])
- TRUE: `{"type": "advantage", "side": "black", "position": "before"}` (engine -1.58 for White)
- to label by hand: 17. Ba1 is a blunder that drops the evaluation from -0.56 to -3.25.
- to label by hand: 17. Ne5 is the best move for White at this position.
- to label by hand: The engine line after 17. Ne5 is 17... Bxe5 18. dxe5 Qh4 19. Rf1 Ng5.
- to label by hand: 17. Ba1 allows Black to consolidate their advantage.

## grounded · https://lichess.org/BcAhQn3U · ply 70 · Black played Qxc4, engine best Qxd7

FEN before: `2r2r1k/p2R2p1/1p6/2p1p3/2Q3q1/1P2Pp2/P4P2/1R2K3 b - - 3 35`

> At move 35, Black’s `Qxc4` was a blunder that failed to eliminate White’s dangerous rook on d7. The engine’s preferred `Qxd7` captures the rook, equalizing material and removing the primary attacker. By playing `Qxc4`, Black allowed White to maintain the pressure with `bxc4` while the rook on d7 remains a potent piece. This error missed the opportunity to simplify the position and neutralize White’s active pieces.

- TRUE: `{"type": "hanging", "square": "d7", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "best_move", "move": "Qxd7", "position": "before"}` (engine top 2: ['Qxd7', 'Qg1+'])
- to label by hand: Black played Qxc4 instead of the best move Qxd7.
- to label by hand: The rook on d7 is a dangerous piece for White.
- to label by hand: Qxd7 captures the rook and equalizes material.
- to label by hand: Qxc4 allows White to maintain pressure with the rook on d7.

## grounded · https://lichess.org/BcAhQn3U · ply 85 · White played a4, engine best Kf1

FEN before: `8/7k/1R6/2p1pr2/2P3p1/4Pp2/P4P2/4K3 w - - 0 43`

> The move 43. a4 is a blunder that allows Black to equalize, whereas 43. Kf1 was the engine's best move, maintaining a slight edge. In the position before 43. a4, White had no hanging pieces and was not in check, but the engine evaluated the position as slightly better for Black (-0.06). By playing 43. a4, White missed the opportunity to keep the king safe and active with 43. Kf1, leading to a drop in evaluation to -5.06. The engine's line suggests 43. Kf1 followed by 43... Rf7 44. Kg1 Rd7 45. Kh2 Rd1. The material count remained equal at the time of the move.

- TRUE: `{"type": "best_move", "move": "Kf1", "position": "before", "position_defaulted": true}` (engine top 2: ['Kf1', 'Rb7+'])
- to label by hand: 43. a4 is a blunder that allows Black to equalize.
- to label by hand: 43. Kf1 was the engine's best move, maintaining a slight edge.
- to label by hand: Before 43. a4, White had no hanging pieces and was not in check.
- to label by hand: The engine evaluated the position before 43. a4 as slightly better for Black (-0.06).
- to label by hand: Playing 43. a4 led to a drop in evaluation to -5.06.
- to label by hand: The engine's line for 43. Kf1 is 43... Rf7 44. Kg1 Rd7 45. Kh2 Rd1.
- to label by hand: The material count remained equal at the time of the move.

## grounded · https://lichess.org/BVzBEglH · ply 64 · Black played a3, engine best Rb4

FEN before: `1r6/4k1pp/1rBn1p2/8/p4P2/4PK2/1PRR2PP/8 b - - 2 32`

> The move 32...a3 misses the tactical opportunity of 32...Rb4, which forces 33. Bd5 Rc8 34. Rxc8 Nxc8 35. Rd4 with a significantly higher evaluation. By playing 32...a3, Black allows White to capture with 33. bxa3, leading to a favorable endgame for White where the engine evaluation drops from +1.23 to +4.04. The alternative line with 32...Rb4 maintains pressure and simplifies into a winning knight endgame for Black. White's best response to 32...Rb4 is 33. Bd5, but this still leaves Black with a clear advantage after the exchange on c8.

- TRUE: `{"type": "advantage", "side": "white", "position": "before"}` (engine +1.32 for White)
- TRUE: `{"type": "best_move", "move": "Rb4", "position": "before"}` (engine top 2: ['Rb4', 'Ra6'])
- to label by hand: The engine line 32...Rb4 33. Bd5 Rc8 34. Rxc8 Nxc8 35. Rd4 results in a winning position for Black.
- to label by hand: After 32...a3 33. bxa3, White's advantage increases significantly according to the engine evaluation.

## grounded · https://lichess.org/BVzBEglH · ply 79 · White played Rd6, engine best Ra7

FEN before: `1r3k2/3R2pp/1n3p2/8/P4P2/3B1K2/6PP/8 w - - 3 40`

> By playing 40. Rd6, White missed the winning 40. Ra7, which maintains a decisive +4.27 evaluation compared to the drop to +0.69 after the game move. The rook on d6 is a hanging piece, as noted in the pre-move facts, and its placement allows Black to generate counterplay that White cannot withstand. The engine line 40... Nc8 41. Rc7 Ne7 42. a5 Rb3 demonstrates that White’s actual choice fails to exploit the weakness of Black’s position effectively.

- TRUE: `{"type": "best_move", "move": "Ra7", "position": "before", "position_defaulted": true}` (engine top 2: ['Ra7', 'Rd4'])
- TRUE: `{"type": "hanging", "square": "d7", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "advantage", "side": "white", "position": "before"}` (engine +4.17 for White)
- to label by hand: 40. Ra7 is the best move for White.
- to label by hand: The rook on d7 is hanging in the position before White's move.
- to label by hand: White has a winning advantage (+4.27) before the move 40. Rd6.
- to label by hand: After 40. Rd6, the evaluation drops to +0.69.
- to label by hand: The engine line 40... Nc8 41. Rc7 Ne7 42. a5 Rb3 shows Black's counterplay after 40. Rd6.

## grounded · https://lichess.org/BVzBEglH · ply 94 · Black played Nf8, engine best Rb7

FEN before: `8/3nk1p1/2R2pB1/7P/5PK1/6P1/1r6/8 b - - 0 47`

> On ply 94, Black’s move `Nf8` was a blunder that squandered a decisive advantage, dropping the evaluation from +2.98 to +6.74. The engine identifies `Rb7` as the best move, which maintains pressure and simplifies into a winning endgame. By playing `Nf8`, Black missed the opportunity to consolidate the material edge with precise rook activity.

- TRUE: `{"type": "best_move", "move": "Rb7", "position": "before", "position_defaulted": true}` (engine top 2: ['Rb7', 'Ra2'])
- TRUE: `{"type": "advantage", "side": "white", "position": "before", "position_defaulted": true}` (engine +2.50 for White)
- TRUE: `{"type": "material", "side": "white", "position": "before", "position_defaulted": true}` (material balance +1 for White)
- to label by hand: Black played Nf8 which is graded as a blunder.
- to label by hand: The engine prefers Rb7 at this moment.
- to label by hand: The evaluation dropped from +2.98 to +6.74 after the move sequence, indicating White's advantage increased significantly due to Black's error.

## grounded · https://lichess.org/BVzBEglH · ply 105 · White played h7, engine best Rxd7+

FEN before: `8/3n1R2/3k1pBP/5P2/6K1/6P1/8/1r6 w - - 3 53`

> At ply 105, White’s $h7$ was a blunder that squandered a decisive advantage, dropping the evaluation from $+7.97$ to $0.00$. The engine identifies $Rxd7+$ as the best move, which forces $Kxd7$ and leaves White with a winning bishop and pawn endgame after $h7$. By playing $h7$, White missed the immediate tactical opportunity to eliminate the defender on d7, allowing Black to simplify into a drawn rook endgame with $Ne5+$.

- TRUE: `{"type": "best_move", "move": "Rxd7+", "position": "before"}` (engine top 2: ['Rxd7+', 'Kf4'])
- TRUE: `{"type": "advantage", "side": "white", "position": "before"}` (engine +7.87 for White)
- TRUE: `{"type": "material", "side": "white", "position": "before"}` (material balance +2 for White)
- to label by hand: White had a decisive advantage before move 105.
- to label by hand: The move h7 allowed Black to simplify into a drawn rook endgame.
- to label by hand: Rxd7+ forces Kxd7, leading to a winning bishop and pawn endgame.

## grounded · https://lichess.org/BVzBEglH · ply 152 · Black played Rxf5+, engine best Rg1+

FEN before: `8/6kP/6B1/5PK1/8/8/8/5r2 b - - 8 76`

> At ply 152, Black played `Rxf5+`, which the engine grades as a blunder, dropping the evaluation from 0.00 to +4.15. The engine identified `Rg1+` as the best move, which maintains the draw by forcing perpetual checks or favorable king activity, whereas `Rxf5+` allows White's king to escape the checks and activate its bishop. The position before the move was equal with no immediate threats, but `Rxf5+` missed the tactical resource of the rook check on the first rank. By capturing the pawn, Black allowed White to consolidate and eventually win, as confirmed by the final result.

- TRUE: `{"type": "best_move", "move": "Rg1+", "position": "before"}` (engine top 2: ['Kh8', 'Rg1+'])
- TRUE: `{"type": "advantage", "side": "white", "position": "after"}` (engine +0.97 for White)
- to label by hand: Rxf5+ allows the white king to escape checks and activates the bishop.
- to label by hand: Rg1+ forces perpetual checks or favorable king activity to hold the draw.

## grounded · https://lichess.org/movw8h7M · ply 36 · Black played d4, engine best Bc8

FEN before: `r2q2k1/1b2b1p1/p1n2r1p/1p1p4/8/P2Q1N2/1PB2PPP/R1B2RK1 b - - 1 18`

> The move 18...d4 is a mistake that misses the engine's preferred 18...Bc8, which keeps the advantage at +2.54 compared to +4.96 after the text move. By playing d4, Black fails to consolidate, allowing White to launch a decisive attack with 19. Nh4. The engine line 18...Bc8 19. Nh4 Kf7 20. Re1 Be6 maintains a manageable advantage for White without the sharp tactical complications introduced by ...d4.

- TRUE: `{"type": "best_move", "move": "Bc8", "position": "before", "position_defaulted": true}` (engine top 2: ['Bc8', 'Rxf3'])
- TRUE: `{"type": "advantage", "side": "white", "position": "before", "position_defaulted": true}` (engine +2.62 for White)
- FALSE: `{"type": "material", "side": "white", "position": "before", "position_defaulted": true}` (material balance +0 for White)
- to label by hand: 18...d4 is a mistake.
- to label by hand: The engine evaluation is +2.54 after 18...Bc8.
- to label by hand: The engine evaluation is +4.96 after 18...d4.
- to label by hand: White can play 19. Nh4 after 18...d4.
- to label by hand: The best line is 18...Bc8 19. Nh4 Kf7 20. Re1 Be6.

## grounded · https://lichess.org/movw8h7M · ply 45 · White played Qxh8, engine best Qg4+

FEN before: `r6q/1b1kb1Q1/p1n2r1B/1p6/3p4/PB3N2/1P3PPP/R4RK1 w - - 1 23`

> The engine identifies 23. Qg4+ as the best move, capitalizing on the check to maintain a winning advantage (+6.00), whereas 23. Qxh8 is a blunder that crashes the evaluation to -0.26. By playing Qxh8, White fails to utilize the available checks (Qxe7+, Ne5+, Be6+) and allows Black to simplify into a drawable or slightly better endgame. The hanging pieces in the position (Black rooks on h8/f3, White bishop on b3) were present, but the immediate tactical failure was the missed forcing sequence.

- TRUE: `{"type": "best_move", "move": "Qg4+", "position": "before", "position_defaulted": true}` (engine top 2: ['Qg4+', 'Qxh8'])
- FALSE: `{"type": "in_check", "position": "before"}` (rules)
- FALSE: `{"type": "hanging", "square": "h8", "position": "before", "position_defaulted": true}` (computed from attackers and defenders)
- FALSE: `{"type": "hanging", "square": "f3", "position": "before", "position_defaulted": true}` (computed from attackers and defenders)
- FALSE: `{"type": "hanging", "square": "b3", "position": "before", "position_defaulted": true}` (computed from attackers and defenders)
- TRUE: `{"type": "advantage", "side": "white", "position": "before"}` (engine +5.86 for White)
- FALSE: `{"type": "advantage", "side": "black", "position": "after"}` (engine -0.39 for White)
- to label by hand: White had available checks including Qxe7+, Ne5+, and Be6+ before the move.
- to label by hand: 23. Qxh8 allows Black to simplify the position, resulting in a significant drop in White's winning chances.
- to label by hand: 23. Qg4+ maintains a large material and positional advantage for White.

## grounded · https://lichess.org/movw8h7M · ply 49 · White played gxf3, engine best Bd5

FEN before: `7r/1b1kb1B1/p1n5/1p6/3p4/PB3r2/1P3PPP/R4RK1 w - - 0 25`

> At move 25, White’s choice of $gxf3$ was a mistake that allowed Black’s rook on $h8$ and $f3$ to remain hanging without sufficient compensation, whereas the engine preferred $Bd5$. The position after White's move resulted in a loss of advantage, dropping from -0.42 to -2.15, as White failed to maintain pressure. By playing $Bd5$, White would have maintained a more stable evaluation of -0.42, keeping the initiative. The immediate tactical reality was that White had a hanging bishop on $b3$ and Black had hanging rooks, but $gxf3$ exacerbated White's difficulties.

- TRUE: `{"type": "best_move", "move": "Bd5", "position": "before"}` (engine top 2: ['Bd5', 'Bd1'])
- TRUE: `{"type": "hanging", "square": "h8", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "hanging", "square": "f3", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "hanging", "square": "b3", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "material", "side": "black", "position": "before"}` (material balance -1 for White)
- to label by hand: White's move gxf3 was graded as a mistake.
- to label by hand: The engine evaluation dropped from -0.42 to -2.15 after gxf3.
- to label by hand: Bd5 was the best move for White at move 25.
- to label by hand: The position before move 25 had White at a slight disadvantage.

## grounded · https://lichess.org/movw8h7M · ply 51 · White played f4, engine best Rad1

FEN before: `8/1b1kb1B1/p1n5/1p5r/3p4/PB3P2/1P3P1P/R4RK1 w - - 1 26`

> The move 26. f4 is a mistake that drops the evaluation from -1.31 to -2.90, whereas 26. Rad1 is the best move, maintaining a more stable position. By playing f4, White allows 26... Rh4, which creates immediate threats against the weak f3 pawn and the exposed king, leading to a significant win chance drop. In contrast, 26. Rad1 would have centralized the rook and kept the position complex, preventing Black from easily activating the rook to h4 with such decisive effect.

- FALSE: `{"type": "best_move", "move": "Rad1", "position": "before"}` (engine top 2: ['Rfe1', 'Kh1'])
- TRUE: `{"type": "advantage", "side": "black", "position": "before"}` (engine -1.24 for White)
- to label by hand: 26. f4 is a mistake that drops the evaluation from -1.31 to -2.90.
- to label by hand: 26. Rad1 is the best move.
- to label by hand: 26. f4 allows 26... Rh4.
- to label by hand: 26... Rh4 creates immediate threats against the weak f3 pawn and the exposed king.
- to label by hand: 26... Rh4 leads to a significant win chance drop.
- to label by hand: 26. Rad1 centralizes the rook.

## grounded · https://lichess.org/movw8h7M · ply 52 · Black played Rh4, engine best Rh7

FEN before: `8/1b1kb1B1/p1n5/1p5r/3p1P2/PB6/1P3P1P/R4RK1 b - - 0 26`

> At move 26, Black’s `Rh4` is a blunder that squanders a winning advantage, whereas `Rh7` maintains pressure and prepares to trade active rooks. The engine’s preferred `Rh7` keeps the bishop on g7 under fire while improving Black’s coordination, avoiding the immediate tactical loss of the exchange. By playing `Rh4`, Black allows White to consolidate with `f3`, neutralizing the initiative and allowing White to eventually equalize and win. The position before `Rh4` shows Black up four pawns with a strong attack, but `Rh4` fails to exploit the hanging bishop on b3 or create decisive threats.

- TRUE: `{"type": "best_move", "move": "Rh7", "position": "before"}` (engine top 2: ['Rh7', 'Rh4'])
- TRUE: `{"type": "advantage", "side": "black", "position": "before"}` (engine -2.95 for White)
- FALSE: `{"type": "material", "side": "black", "position": "before"}` (material balance +4 for White)
- to label by hand: Rh7 maintains pressure on the bishop on g7.
- to label by hand: Rh4 allows White to play f3, neutralizing Black's initiative.
- to label by hand: Black is up four pawns before playing Rh4.
- to label by hand: White eventually equalizes and wins after Black's blunder.

## grounded · https://lichess.org/dlymlJeF · ply 43 · White played Ra3, engine best Ne4

FEN before: `2b2rk1/2q1npbp/4p1p1/2p1P2P/1nPp1PP1/2rP4/3NQ1B1/R1B1RNK1 w - - 1 22`

> White's 22. Ra3 is a critical blunder that squanders a +1.33 advantage, dropping the evaluation to -4.45. The engine identifies 22. Ne4 as the best move, which maintains the initiative and leads to a manageable advantage after 22... gxh5 23. Nfg3 hxg4 24. Bd2 Rxd3. By playing Ra3, White fails to utilize the active knight and allows Black to equalize or seize the counterplay. The move is particularly egregious given that White had checks available, including Ne8+, which were ignored in favor of a passive rook lift.

- TRUE: `{"type": "best_move", "move": "Ne4", "position": "before"}` (engine top 2: ['Ne4', 'Nb1'])
- FALSE: `{"type": "mate_in_one", "move": "Ne8+", "position": "before"}` (mates available: none)
- FALSE: `{"type": "mate_in_one", "move": "h6+", "position": "before"}` (mates available: none)
- TRUE: `{"type": "advantage", "side": "white", "position": "before"}` (engine +1.39 for White)
- to label by hand: 22. Ra3 causes a win chance drop of 0.915.
- to label by hand: The engine line 22. Ne4 gxh5 23. Nfg3 hxg4 24. Bd2 Rxd3 keeps the advantage for White.
- to label by hand: White had available checks Ne8+ and h6+ before the move.

## grounded · https://lichess.org/dlymlJeF · ply 60 · Black played Nc8, engine best Nd5

FEN before: `b5k1/4npbp/2q1p1p1/2B1P2P/2PpNPP1/8/3N2Q1/6K1 b - - 0 30`

> Black’s 30...Nc8 is a blunder that leaves the knight on e7 hanging and the pawn on d4 undefended, allowing White to consolidate. The engine’s recommendation, 30...Nd5, actively challenges White’s setup and maintains dynamic counterplay against the center. By retreating the knight to the rim, Black misses the opportunity to exploit the loose d4 pawn and the exposed e7 knight. This error shifts the evaluation from a negligible +0.02 to a decisive +2.34 in White’s favor.

- TRUE: `{"type": "hanging", "square": "e7", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "hanging", "square": "d4", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "best_move", "move": "Nd5", "position": "before"}` (engine top 2: ['Nd5', 'Qxc5'])
- TRUE: `{"type": "advantage", "side": "white", "position": "after"}` (engine +2.25 for White)
- to label by hand: After 30...Nd5, Black maintains dynamic counterplay against the center.
- to label by hand: The move 30...Nc8 allows White to consolidate their advantage.
- to label by hand: The evaluation shifts from +0.02 to +2.34 after the blunder.

## grounded · https://lichess.org/dlymlJeF · ply 68 · Black played Bb4, engine best Bxe4

FEN before: `2n2b2/5pkp/2b1pNp1/4P2P/2PBNPP1/8/8/6K1 b - - 1 34`

> The engine evaluation indicates White is ahead on material at this moment. Black's move 34...Bb4 fails to address the tactical vulnerability of the knight on e4. The correct move is 34...Bxe4, which captures the hanging piece. This exchange neutralizes White's compensation and shifts the evaluation significantly.

- TRUE: `{"type": "material", "side": "white", "position": "before"}` (material balance +1 for White)
- FALSE: `{"type": "hanging", "square": "e4", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "best_move", "move": "Bxe4", "position": "before"}` (engine top 2: ['Bxe4', 'gxh5'])
- to label by hand: Black's move 34...Bb4 fails to address the tactical vulnerability of the knight on e4.
- to label by hand: The correct move is 34...Bxe4, which captures the hanging piece.
- to label by hand: This exchange neutralizes White's compensation and shifts the evaluation significantly.

## grounded · https://lichess.org/dlymlJeF · ply 69 · White played Bc5, engine best h6+

FEN before: `2n5/5pkp/2b1pNp1/4P2P/1bPBNPP1/8/8/6K1 w - - 2 35`

> By playing 35. Bc5, White misses the forced mate and allows Black to survive, whereas 35. h6+ initiates a decisive attack. The engine's line 35. h6+ Kxh6 36. Nd6 Ne7 37. Nxf7+ Kg7 demonstrates a clear mating net that White fails to realize. Black's subsequent blunder 35... Ba5 allows the actual mate-in-4 sequence to commence, but the earlier inaccuracy squandered a much quicker win. The position before the move shows White has a material advantage and available checks, making the non-checking Bc5 a significant error.

- TRUE: `{"type": "best_move", "move": "h6+", "position": "before", "position_defaulted": true}` (engine top 2: ['h6+', 'Nd6'])
- TRUE: `{"type": "material", "side": "white", "position": "before"}` (material balance +1 for White)
- FALSE: `{"type": "in_check", "position": "before"}` (rules)
- to label by hand: 35. Bc5 misses the forced mate-in-4 opportunity.
- to label by hand: 35. h6+ Kxh6 36. Nd6 Ne7 37. Nxf7+ Kg7 is the engine's best line.
- to label by hand: 35... Ba5 allows White to deliver mate in 4.
- to label by hand: White had checks available, including Ne8+ and h6+, before playing Bc5.

## grounded · https://lichess.org/dlymlJeF · ply 70 · Black played Ba5, engine best Bxc5+

FEN before: `2n5/5pkp/2b1pNp1/2B1P2P/1bP1NPP1/8/8/6K1 b - - 3 35`

> The move 35...Ba5 is a blunder that leaves the bishop on b4 hanging, whereas the engine’s 35...Bxc5+ wins the bishop and simplifies into a winning endgame. By playing 35...Ba5, Black allows the bishop to remain on b4 while White’s bishop on c5 is protected, missing the tactical opportunity to trade bishops. The engine line 35...Bxc5+ 36. Nxc5 Nb6 37. Nce4 Nxc4 demonstrates that Black maintains a decisive material and positional advantage after the exchange. In contrast, 35...Ba5 fails to address the hanging piece and blunders the advantage, leading to a forced mate.

- TRUE: `{"type": "hanging", "square": "b4", "position": "before"}` (computed from attackers and defenders)
- TRUE: `{"type": "best_move", "move": "Bxc5+", "position": "before"}` (engine top 2: ['Bxc5+', 'gxh5'])
- TRUE: `{"type": "advantage", "side": "white", "position": "after"}` (engine +99.96 for White)
- to label by hand: 35...Bxc5+ wins the bishop and simplifies into a winning endgame.
- to label by hand: 35...Ba5 leaves the bishop on b4 hanging.
- to label by hand: The line 35...Bxc5+ 36. Nxc5 Nb6 37. Nce4 Nxc4 maintains a decisive advantage for Black.
- to label by hand: 35...Ba5 leads to a forced mate.

## ungrounded · https://lichess.org/ZRLfDc2e · ply 28 · Black played Nxd5, engine best Nfd7

FEN before: `r1b1k2r/1pq1bp2/2pp1npp/p1nPp3/P1B1P2N/BPN4P/2P2PP1/R2QR1K1 b kq - 2 14`

> Nxd5 is a significant error because it allows White to recapture with $cxd5$, after which Black’s knight on d5 becomes a hanging piece on an open file with no adequate defense. The engine’s preferred move, $Nfd7$, instead retreats the knight to a safe square while maintaining control over central squares and preserving the structural integrity of Black’s position. By playing $Nxd5$, Black essentially blunders a piece for no compensation, handing White a decisive material advantage. In contrast, $Nfd7$ keeps the tension manageable and avoids immediate tactical disasters. This mistake transforms a roughly equal endgame into a lost one for Black.

- TRUE: `{"type": "best_move", "move": "Nfd7", "position": "before", "position_defaulted": true}` (engine top 2: ['Nfd7', 'Na6'])
- TRUE: `{"type": "advantage", "side": "white", "position": "before", "position_defaulted": true}` (engine +1.32 for White)
- FALSE: `{"type": "hanging", "square": "d5", "position": "before", "position_defaulted": true}` (computed from attackers and defenders)
- to label by hand: White can recapture on d5 with the c-pawn.
- to label by hand: The knight on d5 is undefended after the exchange.
- to label by hand: Nfd7 retreats the knight to a safe square.
- to label by hand: Nfd7 maintains control over central squares.
- to label by hand: Nxd5 results in blundering a piece.
- to label by hand: Nxd5 hands White a decisive material advantage.

## ungrounded · https://lichess.org/ZRLfDc2e · ply 34 · Black played Qd7, engine best Qd8

FEN before: `r1b1k2r/1pq2p2/2pP2pp/p1p1p3/P1B4b/1PN4P/2P2PP1/R2QR1K1 b kq - 0 17`

> By playing `Qd7`, Black neglects the critical defensive resource required to maintain equilibrium, allowing White to consolidate their spatial advantage. The engine's preferred move `Qd8` is superior because it keeps the queen flexible and avoids potential tempo losses or tactical vulnerabilities associated with the d7 square. Specifically, `Qd7` may expose the queen to future harassment or fail to adequately control key central and diagonal squares compared to the more passive but solid `Qd8`. For a FIDE Master, recognizing that `Qd8` is the best move highlights the importance of piece safety and flexibility over apparent activity. Consequently, the deviation from the engine's top choice represents a subtle but significant loss of precision in position handling.

- TRUE: `{"type": "best_move", "move": "Qd8", "position": "before", "position_defaulted": true}` (engine top 2: ['Qd8', 'Qb6'])
- to label by hand: Black played Qd7.
- to label by hand: Qd7 allows White to consolidate their spatial advantage.
- to label by hand: Qd8 keeps the queen flexible.
- to label by hand: Qd8 avoids potential tempo losses or tactical vulnerabilities associated with the d7 square.
- to label by hand: Qd7 may expose the queen to future harassment.
- to label by hand: Qd7 fails to adequately control key central and diagonal squares compared to Qd8.
- to label by hand: Qd8 is the best move for Black in this position.

## ungrounded · https://lichess.org/BcAhQn3U · ply 33 · White played Ba1, engine best Ne5

FEN before: `2rqr1k1/p4ppp/1pn2bb1/2pp4/3Pn1P1/1P2PN1P/PB1N1PB1/2RQR1K1 w - - 1 17`

> The move Ba1 is a passive retreat that fails to capitalize on the tactical vulnerabilities in the center. Specifically, it ignores the hanging knight on e5, which is undefended and attacked by Black's pieces. In contrast, the engine's best move Ne5 exploits this weakness by placing a piece directly on that vulnerable square, creating immediate threats. This active intervention improves White's position significantly compared to the passive bishop maneuver.

- FALSE: `{"type": "hanging", "square": "e5", "position": "before"}` (no piece on e5)
- to label by hand: Ba1 is a passive retreat.
- to label by hand: Ne5 is the engine's best move.
- to label by hand: Ne5 places a piece on e5, creating immediate threats.

## ungrounded · https://lichess.org/BcAhQn3U · ply 60 · Black played Bf3, engine best Rf8

FEN before: `2r1r1k1/p2R2p1/1p6/2p1p2b/4p2q/1P2P3/P2Q1PB1/1R3K2 b - - 1 30`

> Bf3 is a passive retreat that fails to address the immediate tactical vulnerability of the black rook on c8, which remains undefended and exposed to White's heavy pieces. The engine's recommendation, Rf8, actively defends the eighth rank and prepares to challenge White's dominant rook on d7, thereby neutralizing White's spatial advantage. By ignoring the threat to the c8 rook, Black allows White to maintain or increase their material and positional pressure without contest. This inaccuracy likely costs Black the initiative and leaves the position strategically inferior.

- FALSE: `{"type": "hanging", "square": "c8", "position": "before", "position_defaulted": true}` (computed from attackers and defenders)
- TRUE: `{"type": "best_move", "move": "Rf8", "position": "before", "position_defaulted": true}` (engine top 2: ['Rf8', 'Kh8'])
- FALSE: `{"type": "advantage", "side": "white", "position": "before", "position_defaulted": true}` (engine -5.69 for White)
- to label by hand: Bf3 is a passive retreat.
- to label by hand: The black rook on c8 is undefended and exposed.
- to label by hand: The black rook on c8 is attacked by White's heavy pieces.
- to label by hand: Rf8 actively defends the eighth rank.
- to label by hand: Rf8 prepares to challenge White's rook on d7.
- to label by hand: White has a spatial advantage.
- to label by hand: Black's move allows White to maintain or increase their material and positional pressure.
- to label by hand: Black's move leaves the position strategically inferior.

## ungrounded · https://lichess.org/BcAhQn3U · ply 63 · White played Qf7, engine best Bxf3

FEN before: `2r1r2k/p2R2p1/1p6/2pQp3/4p2q/1P2Pb2/P4PB1/1R3K2 w - - 4 32`

> White’s choice of Qf7 completely overlooks the tactical vulnerability of the bishop on f3, which hangs undefended. The engine correctly identifies Bxf3 as the best move, removing a dangerous active piece and simplifying the position. By ignoring this threat, White allows Black to recover material and neutralize the attack. This oversight transforms a potentially winning advantage into a precarious situation where White must prove compensation. The failure to execute Bxf3 represents a significant misjudgment in prioritizing tactical security over positional pressure.

- TRUE: `{"type": "best_move", "move": "Bxf3", "position": "before"}` (engine top 2: ['Bxf3', 'Qb7'])
- FALSE: `{"type": "hanging", "square": "f3", "position": "before"}` (computed from attackers and defenders)
- FALSE: `{"type": "advantage", "side": "white", "position": "before"}` (engine -1.58 for White)
- to label by hand: Qf7 ignores the threat to the bishop on f3.
- to label by hand: Bxf3 removes a dangerous active piece for Black.
- to label by hand: Bxf3 simplifies the position.
- to label by hand: Allowing Black to capture the bishop recovers material for Black.
- to label by hand: White had a potentially winning advantage before the move.

## ungrounded · https://lichess.org/BcAhQn3U · ply 70 · Black played Qxc4, engine best Qxd7

FEN before: `2r2r1k/p2R2p1/1p6/2p1p3/2Q3q1/1P2Pp2/P4P2/1R2K3 b - - 3 35`

> Black's move Qxc4 is a critical error that fails to address the tactical threat to the queen on c4. By capturing the pawn, Black leaves the queen vulnerable to the rook on d7, which is defended by the queen on c4 in the original position but becomes undefended after the capture. The engine's best move, Qxd7, is superior because it eliminates the active white rook while maintaining the queen's safety. This exchange simplifies the position favorably for Black, avoiding the loss of material that occurs after Qxc4.

- TRUE: `{"type": "best_move", "move": "Qxd7", "position": "before"}` (engine top 2: ['Qxd7', 'Qg1+'])
- FALSE: `{"type": "material", "side": "white", "position": "after"}` (material balance -11 for White)
- to label by hand: Qxc4 allows the white rook on d7 to capture the black queen on c4.
- to label by hand: Qxd7 removes the white rook from the board.
- to label by hand: Qxd7 maintains the black queen's safety.

## ungrounded · https://lichess.org/BcAhQn3U · ply 85 · White played a4, engine best Kf1

FEN before: `8/7k/1R6/2p1pr2/2P3p1/4Pp2/P4P2/4K3 w - - 0 43`

> White's move a4 is a passive pawn push that fails to address the immediate tactical vulnerability of the King on e1. The engine's recommendation, Kf1, is the best move because it places the King in a safer corner, away from the open files and potential checks. By playing a4, White ignores the fact that the King is exposed and potentially hanging if Black can generate a forcing sequence, although in this specific static position, the King is not technically hanging but lacks safety. Kf1 improves the King's position significantly, reducing the risk of back-rank mates or infiltration by Black's rook on e5. This move demonstrates superior king safety principles compared to the aimless pawn move.

- TRUE: `{"type": "best_move", "move": "Kf1", "position": "before", "position_defaulted": true}` (engine top 2: ['Kf1', 'Rb7+'])
- to label by hand: White played a4.
- to label by hand: The engine's best move was Kf1.
- to label by hand: a4 is a passive pawn push.
- to label by hand: a4 fails to address the King's safety on e1.
- to label by hand: Kf1 places the King in a safer corner.
- to label by hand: Kf1 moves the King away from open files and potential checks.
- to label by hand: Playing a4 ignores the King's exposure.
- to label by hand: The King on e1 is not technically hanging in the static position.
- to label by hand: Kf1 reduces the risk of back-rank mates or infiltration by Black's rook on e5.
- to label by hand: Kf1 demonstrates superior king safety principles compared to a4.

## ungrounded · https://lichess.org/BVzBEglH · ply 64 · Black played a3, engine best Rb4

FEN before: `1r6/4k1pp/1rBn1p2/8/p4P2/4PK2/1PRR2PP/8 b - - 2 32`

> Black’s move `...a3` is a positional error that fails to challenge White’s active piece placement. The engine’s best move, `...Rb4`, correctly targets the weak pawn on `a4`, which is currently hanging and undefended. By playing `...a3`, Black allows White to maintain pressure, whereas `...Rb4` would immediately exploit the lack of defense on that square. This correction utilizes the rook’s range to attack a vulnerable target rather than making a minor pawn push.

- TRUE: `{"type": "hanging", "square": "a4", "position": "before", "position_defaulted": true}` (computed from attackers and defenders)
- TRUE: `{"type": "best_move", "move": "Rb4", "position": "before", "position_defaulted": true}` (engine top 2: ['Rb4', 'Ra6'])
- to label by hand: The move ...a3 fails to challenge White's piece placement.
- to label by hand: The engine's move ...Rb4 targets the pawn on a4.
- to label by hand: The pawn on a4 is undefended.

## ungrounded · https://lichess.org/BVzBEglH · ply 79 · White played Rd6, engine best Ra7

FEN before: `1r3k2/3R2pp/1n3p2/8/P4P2/3B1K2/6PP/8 w - - 3 40`

> The move 1. Rd6 is a significant error as it abandons the critical a7-square, allowing Black's rook to activate with 1... Rxa7. By playing 1. Ra7!, White would have maintained a firm grip on the seventh rank, preventing the black rook from becoming active and keeping pressure on Black's pawn structure. This passive placement of the rook on d6 fails to capitalize on White's positional advantages and material edge, which the engine confirms remains superior for White. The missed opportunity to dominate the seventh rank represents a key strategic oversight in this endgame phase.

- TRUE: `{"type": "best_move", "move": "Ra7", "position": "before"}` (engine top 2: ['Ra7', 'Rd4'])
- TRUE: `{"type": "advantage", "side": "white", "position": "before"}` (engine +4.17 for White)
- TRUE: `{"type": "material", "side": "white", "position": "before"}` (material balance +1 for White)
- to label by hand: The move 1. Rd6 allows the black rook to capture on a7.
- to label by hand: Playing 1. Ra7 would have controlled the seventh rank.
- to label by hand: Controlling the seventh rank prevents the black rook from activating.
- to label by hand: White has a material advantage in the position.
- to label by hand: White has a positional advantage due to the potential to dominate the seventh rank.

## ungrounded · https://lichess.org/BVzBEglH · ply 94 · Black played Nf8, engine best Rb7

FEN before: `8/3nk1p1/2R2pB1/7P/5PK1/6P1/1r6/8 b - - 0 47`

> The move ...Nf8 is a passive retreat that fails to address the critical vulnerability of the rook on b2. By moving the knight, Black allows White to maintain pressure without contesting the second rank or the open files effectively. The engine's preferred move, ...Rb7, places the rook on a more active square where it defends the seventh rank and prepares to challenge White's control. This move improves Black's coordination and prevents immediate tactical exploits against the back rank or the weak pawns. Ultimately, ...Nf8 misses the opportunity to create counterplay, leaving Black in a strictly defensive and inferior position.

- TRUE: `{"type": "best_move", "move": "Rb7", "position": "before"}` (engine top 2: ['Rb7', 'Ra2'])
- to label by hand: The move ...Nf8 is a passive retreat.
- to label by hand: ...Nf8 fails to address the vulnerability of the rook on b2.
- to label by hand: ...Nf8 allows White to maintain pressure without contesting the second rank or open files.
- to label by hand: ...Rb7 places the rook on a more active square defending the seventh rank.
- to label by hand: ...Rb7 prepares to challenge White's control.
- to label by hand: ...Nf8 misses the opportunity to create counterplay.
- to label by hand: Black is in a strictly defensive and inferior position after ...Nf8.

## ungrounded · https://lichess.org/BVzBEglH · ply 105 · White played h7, engine best Rxd7+

FEN before: `8/3n1R2/3k1pBP/5P2/6K1/6P1/8/1r6 w - - 3 53`

> White's choice of 1. h7 is a significant error because it misses the immediate tactical win available with 1. Rxd7+. By playing 1. h7, White fails to capture the undefended knight on d7, allowing Black to maintain material equality and defensive resources. In contrast, the engine's recommended 1. Rxd7+ wins a full piece by capturing the hanging knight on d7 while simultaneously delivering check to the black king. This move exploits the fact that the knight is attacked and undefended, securing a decisive material advantage for White. The loss of this piece likely shifts the evaluation from a win for White to a drawn or lost position depending on subsequent play.

- TRUE: `{"type": "best_move", "move": "Rxd7+", "position": "before"}` (engine top 2: ['Rxd7+', 'Kf4'])
- FALSE: `{"type": "hanging", "square": "d7", "position": "before"}` (computed from attackers and defenders)
- FALSE: `{"type": "advantage", "side": "white", "position": "after"}` (engine +0.00 for White)
- TRUE: `{"type": "material", "side": "white", "position": "after"}` (material balance +2 for White)
- to label by hand: White played h7.
- to label by hand: The knight on d7 is undefended.
- to label by hand: 1. Rxd7+ captures the knight on d7.
- to label by hand: 1. Rxd7+ delivers check to the black king.
- to label by hand: 1. Rxd7+ wins a full piece for White.

## ungrounded · https://lichess.org/BVzBEglH · ply 152 · Black played Rxf5+, engine best Rg1+

FEN before: `8/6kP/6B1/5PK1/8/8/8/5r2 b - - 8 76`

Parse problem: JSON block does not parse

> Rxf5+ was a positional error because it allowed White to maintain a solid defensive structure without facing immediate threats. The engine's best move, Rg1+, utilizes a discovered check to disrupt White's king safety and coordinate with Black's remaining pieces. This forcing move creates concrete tactical problems that the passive capture fails to generate. By checking from the first rank, Black increases the pressure on White's limited resources.


## ungrounded · https://lichess.org/movw8h7M · ply 36 · Black played d4, engine best Bc8

FEN before: `r2q2k1/1b2b1p1/p1n2r1p/1p1p4/8/P2Q1N2/1PB2PPP/R1B2RK1 b - - 1 18`

> The move ...d4 is a significant error because it leaves the pawn on d4 hanging and undefended against White's minor pieces. By advancing the pawn, Black fails to address the immediate tactical vulnerability that White can exploit to win material. The engine's preferred response, ...Bc8, is a precise retreat that preserves the bishop's activity while avoiding unnecessary structural weaknesses or tactical traps. This maneuver keeps Black's position solid and maintains counterplay, whereas the pawn push simplifies the position in Black's favor by giving White a free target. Ultimately, ...d4 cedes the initiative and allows White to consolidate a clear advantage through material gain or improved piece coordination.

- FALSE: `{"type": "hanging", "square": "d4", "position": "before", "position_defaulted": true}` (no piece on d4)
- TRUE: `{"type": "best_move", "move": "Bc8", "position": "before", "position_defaulted": true}` (engine top 2: ['Bc8', 'Rxf3'])
- TRUE: `{"type": "advantage", "side": "white", "position": "before", "position_defaulted": true}` (engine +2.62 for White)
- to label by hand: Black played d4.
- to label by hand: The engine's best move was Bc8.

## ungrounded · https://lichess.org/movw8h7M · ply 45 · White played Qxh8, engine best Qg4+

FEN before: `r6q/1b1kb1Q1/p1n2r1B/1p6/3p4/PB3N2/1P3PPP/R4RK1 w - - 1 23`

> White's choice of Qxh8 misses the tactical opportunity presented by the exposed black king. By playing Qg4+, White would have delivered a check that forces immediate defensive concessions or leads to a decisive material gain. The move Qxh8, while capturing a rook, fails to capitalize on the tactical vulnerability and allows Black to consolidate. The engine's recommendation highlights that initiative and forcing moves are superior to simple piece captures in this specific position.

- TRUE: `{"type": "best_move", "move": "Qg4+", "position": "before", "position_defaulted": true}` (engine top 2: ['Qg4+', 'Qxh8'])
- cannot check: `{"type": "position", "value": "before", "position": "before", "position_defaulted": true}` (unknown claim type 'position')
- cannot check: `{"type": "position", "value": "after", "position": "before", "position_defaulted": true}` (unknown claim type 'position')
- to label by hand: White's move Qxh8 captures a rook.
- to label by hand: The engine recommends Qg4+ as the best move.
- to label by hand: Qg4+ delivers a check to the black king.
- to label by hand: Qxh8 fails to capitalize on the tactical vulnerability.
- to label by hand: Qg4+ forces immediate defensive concessions or leads to decisive material gain.
- to label by hand: White is ahead on material after Qxh8.

## ungrounded · https://lichess.org/movw8h7M · ply 49 · White played gxf3, engine best Bd5

FEN before: `7r/1b1kb1B1/p1n5/1p6/3p4/PB3r2/1P3PPP/R4RK1 w - - 0 25`

> White's move gxf3 is a mistake because it fails to utilize the strong outpost on d5. By playing Bd5, White would have placed the bishop on a square that is both safe and highly active, threatening key weaknesses in Black's camp. The engine's suggestion improves White's piece coordination and maintains a positional advantage. In contrast, gxf3 simplifies the position unnecessarily and allows Black to consolidate their structure.

- TRUE: `{"type": "best_move", "move": "Bd5", "position": "before"}` (engine top 2: ['Bd5', 'Bd1'])
- to label by hand: The move gxf3 fails to utilize the strong outpost on d5.
- to label by hand: Bd5 places the bishop on a safe and highly active square.
- to label by hand: Bd5 threatens key weaknesses in Black's camp.
- to label by hand: gxf3 simplifies the position unnecessarily.
- to label by hand: gxf3 allows Black to consolidate their structure.

## ungrounded · https://lichess.org/movw8h7M · ply 51 · White played f4, engine best Rad1

FEN before: `8/1b1kb1B1/p1n5/1p5r/3p4/PB3P2/1P3P1P/R4RK1 w - - 1 26`

> White's choice of f4 is a strategic error that unnecessarily weakens the king's shelter and fails to address the tactical vulnerability of the Bishop on g7. This piece is currently hanging, as it is attacked by Black's Rook on h5 and has no defenders, meaning White risks losing significant material for no compensation. The engine's recommendation, Rad1, is superior because it develops the rook to an active file while keeping the bishop safe, maintaining the material advantage. By ignoring the threat to g7, White allows Black to capture the bishop with Rg5, equalizing or gaining an advantage.

- FALSE: `{"type": "hanging", "square": "g7", "position": "before", "position_defaulted": true}` (computed from attackers and defenders)
- FALSE: `{"type": "best_move", "move": "Rad1", "position": "before", "position_defaulted": true}` (engine top 2: ['Rfe1', 'Kh1'])
- to label by hand: The move f4 weakens White's king safety.
- to label by hand: The Bishop on g7 is attacked by the Rook on h5.
- to label by hand: The Bishop on g7 is undefended.
- to label by hand: Playing f4 allows Black to capture the bishop with Rg5.

## ungrounded · https://lichess.org/movw8h7M · ply 52 · Black played Rh4, engine best Rh7

FEN before: `8/1b1kb1B1/p1n5/1p5r/3p1P2/PB6/1P3P1P/R4RK1 b - - 0 26`

> Rh4 is a significant error as it places the rook on a square where it becomes an easy target for White's bishop on g7, essentially hanging a piece or allowing for immediate tactical exploitation. In contrast, the engine's recommendation, Rh7, actively defends the critical g7 bishop, which is currently under attack by the white bishop and vital for Black's defensive structure. By retreating to h7, Black maintains material balance and prevents White from simplifying the position with a winning exchange or gaining a decisive positional advantage. This move also keeps the rook more flexible for potential counterplay along the seventh rank, whereas Rh4 isolates it and weakens Black's kingside safety.

- TRUE: `{"type": "best_move", "move": "Rh7", "position": "before"}` (engine top 2: ['Rh7', 'Rh4'])
- to label by hand: Rh4 places the rook on a square where it is attacked by the white bishop on g7.
- to label by hand: The rook on h4 is effectively hanging or tactically vulnerable after Rh4.
- to label by hand: The black bishop on g7 is under attack by the white bishop on g7.
- to label by hand: Rh7 defends the black bishop on g7.
- to label by hand: Rh7 prevents White from capturing the bishop on g7.
- to label by hand: Rh7 maintains material balance for Black.
- to label by hand: Rh4 isolates the rook and weakens Black's kingside safety.

## ungrounded · https://lichess.org/dlymlJeF · ply 43 · White played Ra3, engine best Ne4

FEN before: `2b2rk1/2q1npbp/4p1p1/2p1P2P/1nPp1PP1/2rP4/3NQ1B1/R1B1RNK1 w - - 1 22`

> Ra3 is a passive rook lift that fails to address the tactical vulnerability on e4, where the engine identifies Ne4 as the best move. By playing Ne4, White places a piece on a square that is currently attacked by Black's pawn on d5 but defended by White's pawn on f3, creating a temporary tension that White can resolve favorably. The move Ra3 neglects this central opportunity and allows Black to maintain a solid, albeit slightly cramped, position without immediate complications. White's knight on e4 would exert strong pressure on d6 and f6, restricting Black's counterplay.

- TRUE: `{"type": "best_move", "move": "Ne4", "position": "before", "position_defaulted": true}` (engine top 2: ['Ne4', 'Nb1'])
- FALSE: `{"type": "attacked_by_cheaper", "square": "e4", "position": "before", "position_defaulted": true}` (no piece on e4)
- to label by hand: Ra3 is a passive rook lift.
- to label by hand: The engine identifies Ne4 as the best move.
- to label by hand: White's pawn is on f3.
- to label by hand: Black's pawn is on d5.
- to label by hand: Ne4 places a piece on e4.
- to label by hand: The piece on e4 is attacked by the pawn on d5.
- to label by hand: The piece on e4 is defended by the pawn on f3.
- to label by hand: Ne4 exerts pressure on d6.
- to label by hand: Ne4 exerts pressure on f6.

## ungrounded · https://lichess.org/dlymlJeF · ply 60 · Black played Nc8, engine best Nd5

FEN before: `b5k1/4npbp/2q1p1p1/2B1P2P/2PpNPP1/8/3N2Q1/6K1 b - - 0 30`

> Black's move ...Nc8 is a passive retreat that fails to challenge White's strong central grip. The engine's recommendation, ...Nd5, is superior because it actively occupies the key outpost on d5. This square is currently undefended and serves as a perfect base for Black's knight to influence the game. By playing ...Nd5, Black creates immediate counterplay and disrupts White's coordination. In contrast, ...Nc8 leaves Black's position cramped and reactive.

- TRUE: `{"type": "best_move", "move": "Nd5", "position": "before", "position_defaulted": true}` (engine top 2: ['Nd5', 'Qxc5'])
- to label by hand: The move Nc8 is a passive retreat.
- to label by hand: The move Nc8 fails to challenge White's central grip.
- to label by hand: The square d5 is currently undefended.
- to label by hand: The move Nd5 actively occupies the key outpost on d5.
- to label by hand: The move Nd5 serves as a perfect base for Black's knight to influence the game.
- to label by hand: The move Nd5 creates immediate counterplay.
- to label by hand: The move Nd5 disrupts White's coordination.
- to label by hand: The move Nc8 leaves Black's position cramped and reactive.

## ungrounded · https://lichess.org/dlymlJeF · ply 68 · Black played Bb4, engine best Bxe4

FEN before: `2n2b2/5pkp/2b1pNp1/4P2P/2PBNPP1/8/8/6K1 b - - 1 34`

> The move 34...Bb4 is a significant error because it leaves the bishop on b4 undefended and vulnerable to capture, whereas the engine's recommendation 34...Bxe4 actively wins a central pawn. By playing 34...Bb4, Black fails to exploit the tactical opportunity presented by the pinned and overloaded white pieces, specifically the bishop on e4 which is attacked by the black bishop on c6. The engine line 34...Bxe4 removes a strong white piece and improves Black's material balance, creating a more favorable endgame structure compared to the passive and risky 34...Bb4.

- FALSE: `{"type": "hanging", "square": "b4", "position": "before", "position_defaulted": true}` (no piece on b4)
- TRUE: `{"type": "best_move", "move": "Bxe4", "position": "before", "position_defaulted": true}` (engine top 2: ['Bxe4', 'gxh5'])
- to label by hand: The move 34...Bb4 leaves the bishop on b4 undefended and vulnerable to capture.
- to label by hand: The engine's recommendation 34...Bxe4 actively wins a central pawn.
- to label by hand: Black fails to exploit the tactical opportunity presented by the pinned and overloaded white pieces.
- to label by hand: The bishop on e4 is attacked by the black bishop on c6.
- to label by hand: The engine line 34...Bxe4 removes a strong white piece and improves Black's material balance.
- to label by hand: The passive and risky 34...Bb4 creates a less favorable endgame structure compared to 34...Bxe4.

## ungrounded · https://lichess.org/dlymlJeF · ply 69 · White played Bc5, engine best h6+

FEN before: `2n5/5pkp/2b1pNp1/4P2P/1bPBNPP1/8/8/6K1 w - - 2 35`

> White's choice of Bc5 was a passive error that missed the tactical opportunity to open lines against the black king. The engine's best move, h6+, forces a decisive structural weakness by compelling Black to respond with ...gxh6. This sacrifice shatters the pawn shield around the black king, exposing it to immediate mating threats that the bishop on c5 fails to exploit. By allowing the king to remain sheltered, White squanders a clear winning advantage.

- TRUE: `{"type": "best_move", "move": "h6+", "position": "before"}` (engine top 2: ['h6+', 'Nd6'])
- TRUE: `{"type": "advantage", "side": "white", "position": "before"}` (engine +4.08 for White)
- TRUE: `{"type": "material", "side": "white", "position": "before"}` (material balance +1 for White)
- to label by hand: Bc5 is a passive move.
- to label by hand: h6+ forces Black to play ...gxh6.
- to label by hand: gxh6 shatters the pawn shield around the black king.
- to label by hand: The exposed black king faces immediate mating threats.
- to label by hand: White has a clear winning advantage.
- to label by hand: Bc5 fails to exploit the tactical opportunity.

## ungrounded · https://lichess.org/dlymlJeF · ply 70 · Black played Ba5, engine best Bxc5+

FEN before: `2n5/5pkp/2b1pNp1/2B1P2P/1bP1NPP1/8/8/6K1 b - - 3 35`

> Ba5 is a passive retreat that fails to address the tactical vulnerability on c5. The engine's best move, Bxc5+, forces an immediate exchange that exposes White's king or simplifies into a favorable endgame. By playing Ba5, Black allows White to maintain a strong bishop on c5 which restricts Black's pieces. The tactical shot Bxc5+ is superior because it utilizes the bishop's activity to create immediate threats. This move highlights the importance of active piece play over passive maneuvering in complex middlegames.

- TRUE: `{"type": "best_move", "move": "Bxc5+", "position": "before"}` (engine top 2: ['Bxc5+', 'gxh5'])
- to label by hand: Ba5 is a passive retreat.
- to label by hand: Bxc5+ forces an immediate exchange.
- to label by hand: White has a bishop on c5 before Black's move.
- to label by hand: Black's bishop was on c6 before the move Ba5.
- to label by hand: White's bishop on c5 is attacked by Black's bishop on c6 before the move Ba5.
