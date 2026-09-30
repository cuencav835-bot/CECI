# Prompts listos para herramientas gratuitas (Kling, Google Flow, Hailuo, Pika, Luma)

Uso: genera cada escena en **16:9, 720p, 5–6 s, sin audio**, con la **imagen de referencia** del grupo indicado (image-to-video). Guarda como `clips/E01.mp4 … E25.mp4`. `producir.py` repite el clip si la narración dura más; si quieres más variedad, genera una segunda toma y cambia el nombre (E07b) antes de ajustar `escenas.json`.

Sufijo obligatorio en TODOS los prompts (ya incluido abajo como `[SUFIJO]`):
`3D Pixar-like kids cartoon, vivid colors, warm soft light, slow smooth camera, same character design throughout, no text, no logos, no watermark, nothing scary.`

## Imágenes de referencia (genera una por grupo y reutilízala siempre)
- **R1 patitos:** yellow mother duck with a small pink bow and exactly five identical small fluffy yellow ducklings with orange beaks, standing in a row on a pastel green background, full body, [SUFIJO]
- **R2 familia:** cartoon family, dad red shirt, mom blue dress, brother green t-shirt, sister yellow dress, baby pink onesie, standing together, full body, pastel background, [SUFIJO]
- **R3 autobús:** big friendly yellow school bus with a smile, plus a cow, horse, pig, lamb and a gentle smiling tiger, pastel background, [SUFIJO]
- **R4 monitos:** exactly five identical little brown monkeys in colorful pajamas and a kind cartoon doctor in a white coat, pastel background, [SUFIJO]
- **R5 tren:** smiling red, yellow and blue toy train with baby farm animals (calf, foal, lamb, duckling, piglet) and a mother cow, pastel background, [SUFIJO]

## Clips (E = escena; R = referencia)
| Escena | Ref | Prompt |
|---|---|---|
| E01 intro | R1 | Mother duck and five ducklings wave hello to the camera on a sunny flower meadow with a rainbow |
| E02 | R1 | Mother duck leads five ducklings along a green path up a gentle hill, camera follows from behind |
| E03 | R1 | Exactly four ducklings walk back to mother duck, clearly countable |
| E04 | R1 | Five ducklings slide and waddle down the hill, flapping tiny wings |
| E05 | R1 | Five ducklings run happily to mother duck, then the family walks toward a soft sunset |
| E06 | R1 | Five ducklings step forward one at a time into a row, hopping gently, slow and clear |
| E07 | R2 | Dad next to a red apple and red ball, mom next to blue balloons and blue sky, both smiling |
| E08 | R2 | Brother on green grass holding a green leaf, sister by a yellow sun toy, baby with pink cotton candy |
| E09 | R2 | The whole family walks across a rainbow and points at colorful objects |
| E10 | R2 | Each family member holds up one object: red apple, blue balloon, green leaf, yellow toy, pink flower |
| E11 | R3 | The yellow bus drives through a colorful small town, wheels turning, cows move happily inside |
| E12 | R3 | Lambs hop gently inside the bus and a friendly smiling tiger waves, bus crosses a small bridge |
| E13 | R3 | All animals dance inside the bus and wave from the windows, sunset road |
| E14 | R3 | Cow, horse, pig, lamb and tiger appear one at a time in front of the bus, each moving clearly |
| E15 | R4 | Five monkeys play on a big safe bed, then four play while one sits, then three jump |
| E16 | R4 | One monkey plays alone, the kind doctor appears and reminds them gently, monkeys play on the floor |
| E17 | R4 | Five monkeys lie in their little beds under soft night light, smile and fall asleep, slow push-in |
| E18 | R1 | Ducklings peek out from behind flowers and trees in a colorful park, hide and seek |
| E19 | R5 | Toy train arrives at a station, mother cow waits, three colorful doors, the third opens to a calf |
| E20 | R5 | Train visits a horse station and finds a foal, then a sheep station and finds a lamb |
| E21 | R5 | All baby animals ride together in the smiling train and wave happily through the countryside |
| E22 | R2 | Family finds a basket of colorful water balloons in a sunny garden, each holds one |
| E23 | R2 | Family plays safely with balloons, bubbles and confetti, then gathers under a rainbow |
| E24 | R1+R2 | Ducklings and family dance together: clap, jump, wave arms, spin |
| E25 outro | R1+R2 | Family and ducklings wave goodbye on a meadow at sunset with balloons and butterflies |

Nota: si una herramienta solo admite una imagen de referencia, en E24/E25 usa R2 y añade "with a mother duck and five ducklings" al prompt, y revisa que los personajes no cambien.
