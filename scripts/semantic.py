#!/usr/bin/env python3
"""Shared semantic tagger for the LoRA KBs (identical copy in image-lora-kb and video-lora-kb).

One lexicon is used twice:
  * on catalog entries (name, slug, triggers, CivitAI tags, description) -> `semantic` tags per category
  * on a draft prompt -> the same tags, so suggest.py can match prompt intent to LoRAs.

Categories: subject, concept, clothing, expression, object, pose, style, anatomy, motion.
Tags are canonical lower-case words. Nothing here invents triggers or strengths.
Adults only: `blocked()` rejects minor-coded / school-coded text before anything is catalogued.
"""
from __future__ import annotations
import math, re

CATEGORIES = ["subject", "concept", "clothing", "expression", "object", "pose", "style", "anatomy", "motion"]
CATEGORY_LABEL = {"subject": "subject/character", "concept": "concept/intent", "clothing": "clothing/outfit",
                  "expression": "expression", "object": "object/prop", "pose": "pose/action/camera",
                  "style": "style/medium", "anatomy": "anatomy", "motion": "video motion"}

# (canonical tag, regex of synonyms). Regexes run on lower-cased text where "_" and "-" became spaces.
L = {
"subject": [
 ("woman", r"\b(woman|women|girl|girls|female|lady|ladies|1girl|2girls|3girls|wife|milf|waifu|mature female)\b"),
 ("man", r"\b(man|men|male|guy|boy ?friend|husband|1boy|2boys|dilf|mature male|daddy)\b"),
 ("couple", r"\b(couple|lovers|hetero|1boy 1girl|1girl 1boy|boyfriend girlfriend)\b"),
 ("group", r"\b(group|crowd|orgy|gangbang|threesome|foursome|harem|multiple (girls|boys|people)|team)\b"),
 ("futanari", r"\b(futa\w*|dickgirl|shemale|trans ?(woman|girl)|newhalf)\b"),
 ("femboy", r"\b(femboy|trap|crossdress\w*|sissy)\b"),
 ("mature", r"\b(milf|mature|gilf|older (woman|man)|cougar|middle aged|grandma|granny)\b"),
 ("muscular", r"\b(muscular|bodybuilder|fitness|muscle (girl|man)|abs|athletic|buff)\b"),
 ("bbw", r"\b(bbw|plus size|chubby|fat|thick|curvy|voluptuous|plump|ssbbw|obese)\b"),
 ("petite", r"\b(petite|slim|skinny|slender|small frame)\b"),
 ("giantess", r"\b(giantess|giant woman|macro|size difference|shrunk|tiny (people|man|person)|micro)\b"),
 ("elf", r"\b(elf|elves|elven|dark elf|high elf|pointy ears)\b"),
 ("demon", r"\b(demon|succubus|devil|incubus|imp|horns)\b"),
 ("angel", r"\b(angel|halo|feathered wings)\b"),
 ("vampire", r"\b(vampire|vampiric)\b"),
 ("monster", r"\b(monster|creature|beast|orc|goblin|troll|ogre|tentacle monster|slime|alien|xenomorph|werewolf|minotaur|kaiju)\b"),
 ("monster girl", r"\b(monster girl|monstergirl|lamia|harpy|centaur|arachne|mermaid|kitsune|slime girl|dragon girl)\b"),
 ("furry", r"\b(furry|anthro|kemono|fursona|feral|scalie|protogen)\b"),
 ("animal ears", r"\b(cat ?girl|catgirl|neko|fox ?girl|bunny ?girl|wolf ?girl|kemonomimi|animal ears|cat ears|dog ?girl|cow ?girl ears)\b"),
 ("robot", r"\b(robot|android|cyborg|mecha|mech|gynoid|droid|automaton)\b"),
 ("zombie", r"\b(zombie|undead|ghoul|ghost|skeleton|lich)\b"),
 ("witch", r"\b(witch|sorceress|mage|wizard|warlock|sorcerer)\b"),
 ("warrior", r"\b(warrior|knight|samurai|soldier|paladin|barbarian|gladiator|amazon(ess)?|valkyrie|ninja|assassin)\b"),
 ("superhero", r"\b(superhero|super hero|supergirl|wonder woman|batgirl|catwoman|harley quinn|marvel|dc comics|avengers|spider ?(man|woman|gwen)|villainess|supervillain)\b"),
 ("princess", r"\b(princess|queen|empress|royalty|noble ?woman)\b"),
 ("nun", r"\b(nun|priestess|shrine maiden|miko|cleric)\b"),
 ("pirate", r"\b(pirate|buccaneer)\b"),
 ("cowgirl western", r"\b(cowboy|western|wild west|rancher)\b"),
 ("celebrity", r"\b(celebrity|actress|actor|singer|pornstar|porn star|influencer|model likeness|real person|instagram model|onlyfans|youtuber|streamer|cosplayer)\b"),
 ("game character", r"\b(genshin|honkai|zenless|zzz|nikke|blue archive|overwatch|league of legends|final fantasy|ffvii|ffxiv|resident evil|street fighter|tekken|mortal kombat|elden ring|dark souls|witcher|mass effect|cyberpunk 2077|fire emblem|persona|xenoblade|nier|tomb raider|metroid|zelda|mario|sonic|pokemon|warcraft|world of warcraft|starcraft|azur lane|arknights|fate grand order|fgo|wuthering waves|valorant|apex legends|baldur|dota|street fighter|bayonetta|devil may cry|silent hill|halo|gears of war|destiny|borderlands|fortnite|helldivers|stellar blade|goddess of victory)\b"),
 ("anime character", r"\b(one piece|naruto|bleach|dragon ball|jujutsu|chainsaw man|spy x family|attack on titan|evangelion|gundam|one punch|my hero|jojo|hunter x hunter|fairy tail|sword art|re ?zero|konosuba|overlord|frieren|dandadan|oshi no ko|vtuber|hololive|nijisanji|taimanin|kill la kill|gurren|darling in the franxx|code geass|fullmetal|cowboy bebop|ghost in the shell|lupin|rosario|highschool|to love ru|prison school|monogatari|danmachi|goblin slayer|shield hero|mushoku|rance|queen.?s blade|ikkitousen|sailor moon|precure|lycoris|bocchi|chainsaw)\b"),
 ("cartoon character", r"\b(disney|pixar|dreamworks|simpsons|family guy|futurama|south park|rick and morty|avatar|legend of korra|kim possible|totally spies|scooby|looney|tiny toons|ben 10|adventure time|regular show|steven universe|she ra|winx|my little pony|gravity falls|star vs|the owl house|helluva boss|hazbin hotel|incredibles|frozen|elsa|jessica rabbit|gargoyles|x ?men evolution|danny phantom)\b"),
 ("original character", r"\b(oc|original character|self trained identity|my character)\b"),
],
"concept": [
 ("sex", r"\b(sex|sexual intercourse|fucking|fuck|penetrat\w*|vaginal|intercourse|coitus|hetero sex|mating)\b"),
 ("oral", r"\b(blowjob|blow job|fellatio|oral|deepthroat|deep throat|irrumatio|cunnilingus|face ?fuck|throat ?fuck|ball (licking|sucking)|rimjob|rimming|anilingus|licking (penis|pussy))\b"),
 ("anal", r"\b(anal|ass ?fuck|butt ?sex|sodomy|anal sex)\b"),
 ("handjob", r"\b(handjob|hand job|stroking|jerking|jerk off|milking)\b"),
 ("titjob", r"\b(titjob|tit ?fuck|paizuri|boobjob|breast sex)\b"),
 ("footjob", r"\b(footjob|foot ?job|foot worship|feet worship)\b"),
 ("masturbation", r"\b(masturbat\w*|fingering|self pleasure|touching herself|solo female|frigging|schlick)\b"),
 ("cumshot", r"\b(cum\w*|semen|sperm|facial|bukkake|creampie|ejaculat\w*|gokkun|cum ?shot|cum on|cum in|load)\b"),
 ("squirt", r"\b(squirt\w*|female ejaculation|pussy juice|wet pussy|dripping)\b"),
 ("orgasm", r"\b(orgasm\w*|climax\w*|ahegao|cumming|trembling|shaking legs)\b"),
 ("bdsm", r"\b(bdsm|bondage|shibari|kinbaku|rope|restrain\w*|tied up|bound|domination|submissi\w*|dominatrix|femdom|maledom|slave|spanking|whip\w*|flogg\w*|discipline|punishment)\b"),
 ("groupsex", r"\b(gangbang|gang bang|orgy|threesome|foursome|mmf|ffm|spitroast|spit ?roast|double penetration|\bdp\b|airtight|group sex|bukkake|train)\b"),
 ("lesbian", r"\b(lesbian|yuri|girl on girl|scissoring|tribadism|sapphic|two women kissing)\b"),
 ("gay", r"\b(gay|yaoi|bara|male on male|homo)\b"),
 ("kissing", r"\b(kiss\w*|french kiss|making out|tongue kiss)\b"),
 ("pregnancy", r"\b(pregnan\w*|impregnat\w*|baby bump|preggo|lactat\w*|breast milk|milking breasts)\b"),
 ("exhibitionism", r"\b(exhibition\w*|public (sex|nudity)|flashing|voyeur\w*|caught|upskirt|downblouse|nip slip|wardrobe malfunction|accidental exposure|nudist|naturist|candid nude)\b"),
 ("nudity", r"\b(nude|naked|nudity|topless|bottomless|completely nude|undress\w*|stripping|striptease|strip)\b"),
 ("tentacles", r"\b(tentacle\w*|octopus|kraken)\b"),
 ("transformation", r"\b(transform\w*|tf|morph\w*|bimbofication|bimbo|corruption|mind ?control|hypno\w*|brainwash\w*|possession|petrif\w*|inflation|expansion|growth|shrink\w*)\b"),
 ("size difference", r"\b(size difference|giantess|shrunk|tiny|micro|macro|vore|unbirth|height difference)\b"),
 ("toys", r"\b(dildo|vibrator|sex toy|buttplug|butt plug|anal beads|fleshlight|sex machine|fucking machine|magic wand|hitachi|strap ?on|onahole)\b"),
 ("condom", r"\b(condom\w*|used condom|rubber)\b"),
 ("chastity", r"\b(chastity|cage|locked)\b"),
 ("feet fetish", r"\b(feet|foot fetish|soles|toes|barefoot|foot focus)\b"),
 ("lactation", r"\b(lactat\w*|breast milk|milking|nursing)\b"),
 ("watersports", r"\b(pee|peeing|piss|pissing|urinat\w*|golden shower)\b"),
 ("medical", r"\b(medical|doctor|nurse|hospital|exam\w*|gyno\w*|speculum|cross ?section|x ?ray|anatomy chart|clinical|surgery|surgical|catheter|ultrasound|internal view)\b"),
 ("horror", r"\b(horror|gore|blood|creepy|scary|eldritch|lovecraft\w*|nightmare|haunted|dark fantasy|grim|macabre)\b"),
 ("fantasy", r"\b(fantasy|magic|sorcery|dragon|fairy|faerie|mythical|medieval|dungeon|enchanted)\b"),
 ("sci-fi", r"\b(sci ?fi|science fiction|cyberpunk|space|spaceship|futuristic|alien|android|mecha|starship|dystopia|retrofuturism|space ?suit)\b"),
 ("romance", r"\b(romantic|romance|love|intimate|tender|cuddl\w*|wedding|bride|honeymoon)\b"),
 ("fitness", r"\b(gym|workout|fitness|yoga|exercise|sweat\w*|sports|athlete)\b"),
 ("beach", r"\b(beach|seaside|ocean|pool|poolside|swimming|tropical|island)\b"),
 ("nightlife", r"\b(club|nightclub|party|rave|bar|stripper|strip club|pole danc\w*|lap dance)\b"),
 ("office", r"\b(office|secretary|boss|ceo|business|corporate|meeting room|desk)\b"),
 ("domestic", r"\b(bedroom|bed|kitchen|bathroom|shower|bath|living room|couch|sofa|home|apartment|laundry)\b"),
 ("outdoors", r"\b(outdoor\w*|forest|park|garden|field|meadow|mountain|street|city|urban|alley|rooftop|parking|car park|camping|nature)\b"),
 ("vehicle", r"\b(car|truck|motorcycle|bike|train|bus|subway|airplane|plane|boat|ship|spaceship|limo|taxi|back seat)\b"),
 ("cosplay", r"\b(cosplay\w*|costume|dress up|halloween)\b"),
 ("humiliation", r"\b(humiliat\w*|degradat\w*|cuck\w*|ntr|netorare|cheating|blackmail)\b"),
 ("worship", r"\b(worship\w*|ass worship|cock worship|body worship|smother\w*|facesit\w*|face sitting|queening)\b"),
 ("wet", r"\b(wet|soaked|drenched|rain|oiled|oily|glistening|sweaty|slime|goo|messy)\b"),
 ("aftermath", r"\b(after ?sex|aftermath|afterglow|exhausted|cum drip\w*|messy hair|used|lying after)\b"),
 ("realism enhancement", r"\b(realism|realistic|photoreal\w*|lifelike|skin detail|skin texture|pores|natural skin|amateur|candid|raw photo)\b"),
 ("detail enhancement", r"\b(detail\w*|enhanc\w*|sharp\w*|quality|aesthetic|refin\w*|hires|high res|masterpiece|best quality|clarity)\b"),
 ("speed", r"\b(turbo|lightning|distill\w*|hyper|lcm|dmd2?|few ?step|4 ?step|8 ?step|lightx2v|causvid|accelerat\w*|fast|speed)\b"),
 ("slider", r"\b(slider|adjuster|tweaker|control lora|weight slider)\b"),
 ("character sheet", r"\b(character sheet|reference sheet|turnaround|multiple views|multi ?view|model sheet|expression sheet|concept art sheet)\b"),
 ("text and logos", r"\b(text|typography|lettering|logo|poster|sign|caption|speech bubble|title card|magazine cover)\b"),
 ("background", r"\b(background|scenery|environment|landscape|interior|room|architecture|cityscape|backdrop|location)\b"),
 ("lighting", r"\b(light\w*|neon|sunset|sunrise|golden hour|backlit|rim light|chiaroscuro|volumetric|god rays|candle ?light|moonlight|low key|high key|shadow\w*|glow\w*|bokeh|flash)\b"),
],
"clothing": [
 ("lingerie", r"\b(lingerie|underwear|teddy|babydoll|negligee|chemise|bralette|bustier|garter belt|garters?|panties|panty|thong|g ?string|bra|knickers|boyshorts)\b"),
 ("latex", r"\b(latex|rubber suit|pvc|vinyl|shiny suit|catsuit|gimp)\b"),
 ("leather", r"\b(leather|biker jacket)\b"),
 ("bodysuit", r"\b(bodysuit|body suit|leotard|unitard|plugsuit|zentai|onesie|jumpsuit)\b"),
 ("corset", r"\b(corset|waist cincher|bustier)\b"),
 ("stockings", r"\b(stocking\w*|thigh ?highs?|pantyhose|tights|nylons?|fishnet\w*|garter\w*|over the knee socks|socks|leggings)\b"),
 ("heels", r"\b(heels?|high heels|stilettos?|pumps|platform\w*|boots?|thigh boots|shoes?|sandals?|sneakers?|footwear)\b"),
 ("swimwear", r"\b(bikini|swimsuit|swimwear|one piece swimsuit|micro bikini|monokini|bathing suit|sling ?shot)\b"),
 ("dress", r"\b(dress|gown|evening gown|sundress|cocktail dress|wedding dress|maxi|mini ?dress|qipao|cheongsam|ao dai)\b"),
 ("skirt", r"\b(skirt|miniskirt|microskirt|pleated|pencil skirt)\b"),
 ("shorts jeans", r"\b(shorts|jeans|denim|daisy dukes|hot pants|yoga pants|leggings|trousers|pants|sweatpants)\b"),
 ("top", r"\b(shirt|t ?shirt|tank top|crop top|blouse|tube top|sweater|hoodie|turtleneck|cardigan|halter|camisole|tee)\b"),
 ("jacket coat", r"\b(jacket|coat|trench ?coat|blazer|parka|cloak|cape)\b"),
 ("uniform", r"\b(uniform|maid|nurse outfit|police|cop|military|soldier|stewardess|flight attendant|waitress|cheerleader|referee|secretary outfit|office lady|business suit|suit and tie|scrubs|chef|pilot)\b"),
 ("maid", r"\b(maid|french maid|maid outfit|maid headdress)\b"),
 ("bunny suit", r"\b(bunny ?suit|playboy bunny|bunny girl|reverse bunny)\b"),
 ("armor", r"\b(armor|armour|bikini armor|plate armor|power armor|knight armor|pauldron|gauntlets?)\b"),
 ("traditional", r"\b(kimono|yukata|hanfu|sari|saree|dirndl|hanbok|qipao|cheongsam|toga|chiton|harem outfit|belly dancer)\b"),
 ("costume", r"\b(costume|cosplay|outfit|superhero suit|halloween costume|fantasy outfit)\b"),
 ("sportswear", r"\b(sportswear|gym clothes|sports bra|yoga|tracksuit|jersey|athletic wear|spandex|bike shorts|tennis)\b"),
 ("sleepwear", r"\b(pajamas?|pyjamas?|nightgown|nightie|sleepwear|robe|bathrobe|towel)\b"),
 ("see-through", r"\b(see ?through|sheer|transparent|wet clothes|mesh|lace|translucent)\b"),
 ("revealing", r"\b(revealing|cleavage cutout|underboob|sideboob|cutout|backless|plunging|skimpy|micro|slingshot|pasties|nipple covers|tape)\b"),
 ("harness", r"\b(harness\w*|straps|body harness|chest harness)\b"),
 ("gloves", r"\b(gloves?|elbow gloves|opera gloves|mittens)\b"),
 ("headwear", r"\b(hat|cap|beret|crown|tiara|headband|veil|hood|helmet|witch hat|cowboy hat|bunny ears|hair ornament|hairband)\b"),
 ("eyewear", r"\b(glasses|sunglasses|goggles|eyewear|monocle|spectacles)\b"),
 ("mask", r"\b(mask|masked|gas mask|blindfold|ball gag|gag|muzzle|balaclava)\b"),
 ("jewelry", r"\b(jewel\w*|necklace|earrings?|bracelet|choker|piercing\w*|nipple rings?|navel piercing|anklet|ring)\b"),
 ("collar", r"\b(collar|leash|choker)\b"),
 ("apron", r"\b(apron|naked apron)\b"),
 ("clothes pulled", r"\b(clothes (pulled|lift)\w*|shirt lift|skirt lift|panties aside|pulled down|clothing aside|undressing|half dressed|partially clothed|unbuttoned|open shirt|torn clothes)\b"),
 ("nude", r"\b(nude|naked|topless|bottomless|no clothes)\b"),
],
"expression": [
 ("smile", r"\b(smil\w*|grin|grins|grinning|happy|cheerful|laugh\w*|joyful)\b"),
 ("seductive", r"\b(seductive|sultry|bedroom eyes|flirt\w*|alluring|teasing|naughty|smirk\w*|lustful|come hither)\b"),
 ("ahegao", r"\b(ahegao|fucked silly|rolling eyes|eyes rolled|tongue out|crossed eyes|mind break)\b"),
 ("pleasure", r"\b(pleasure|moan\w*|ecstasy|ecstatic|aroused|horny|panting|open mouth|heavy breathing|blush\w*|orgasm face|o face)\b"),
 ("pain crying", r"\b(cry|cries|crying|tears|teary|sobbing|pain|wince|grimace)\b"),
 ("angry", r"\b(angry|anger|furious|rage|glare|frown\w*|annoyed|scowl)\b"),
 ("sad", r"\b(sad|melancholy|depressed|gloomy|sorrow)\b"),
 ("surprised", r"\b(surprise\w*|shock\w*|startled|gasp\w*|wide eyes|embarrass\w*)\b"),
 ("shy", r"\b(shy|bashful|embarrassed|nervous|flustered|blushing)\b"),
 ("bored", r"\b(bored|unamused|deadpan|expressionless|blank stare|neutral expression|tired)\b"),
 ("smug", r"\b(smug|confident|cocky|mischievous|evil smile|yandere|crazy|psycho)\b"),
 ("eye contact", r"\b(eye contact|looking at viewer|looking at camera|staring)\b"),
 ("talking", r"\b(talk\w*|speak\w*|speech|lip ?sync|dialogue|whisper\w*|singing|voice)\b"),
 ("facial expression", r"\b(expression\w*|emotion\w*|face(s|ial)? expression|facial)\b"),
],
"object": [
 ("bed", r"\b(bed|bedsheets|pillow\w*|mattress)\b"),
 ("chair", r"\b(chair|stool|throne|sofa|couch|bench)\b"),
 ("table desk", r"\b(table|desk|counter|bar counter)\b"),
 ("mirror", r"\b(mirror|reflection)\b"),
 ("phone", r"\b(phone|smartphone|iphone|selfie|cellphone|camera phone)\b"),
 ("camera", r"\b(camera|polaroid|dslr|webcam|camcorder|cctv|security camera|bodycam|gopro)\b"),
 ("weapon", r"\b(sword|katana|gun|pistol|rifle|weapon|spear|axe|bow and arrow|dagger|knife|staff|scythe|whip)\b"),
 ("food", r"\b(food|fruit|banana|cake|ice cream|chocolate|candy|popsicle|lollipop|cream|whipped cream|cooking|wine|beer|coffee|cocktail|drink)\b"),
 ("rope", r"\b(rope\w*|shibari|bondage rope)\b"),
 ("restraints", r"\b(handcuff\w*|cuffs|shackles?|chains?|stocks|pillory|spreader bar|straitjacket|cage)\b"),
 ("dildo", r"\b(dildo\w*|strap ?on|horse dildo)\b"),
 ("vibrator", r"\b(vibrator|magic wand|hitachi|egg vibrator|remote vibrator)\b"),
 ("plug", r"\b(butt ?plug|anal plug|tail plug|anal beads)\b"),
 ("machine", r"\b(sex machine|fucking machine|milking machine|machine)\b"),
 ("condom", r"\b(condom\w*)\b"),
 ("cock ring", r"\b(cock ?ring\w*|penis ring)\b"),
 ("vehicle", r"\b(car|motorcycle|truck|bike|train|bus|boat|spaceship)\b"),
 ("pole", r"\b(stripper pole|pole)\b"),
 ("glory hole", r"\b(glory ?hole|stuck in wall|through wall|wall)\b"),
 ("tentacle", r"\b(tentacle\w*)\b"),
 ("plant flower", r"\b(flower\w*|rose\w*|plant\w*|vines?|petals|bouquet)\b"),
 ("water", r"\b(water|bath\w*|shower|pool|hot tub|jacuzzi|onsen|bathtub|ocean|lake|river)\b"),
 ("book", r"\b(book|magazine|newspaper|comic book)\b"),
 ("instrument", r"\b(guitar|piano|violin|instrument|microphone)\b"),
 ("toy", r"\b(toy|plush|doll|teddy bear|figurine|balloon)\b"),
 ("medical tool", r"\b(speculum|syringe|stethoscope|catheter|gyno chair|exam table|enema)\b"),
 ("sign text", r"\b(sign|poster|banner|text|logo|placard)\b"),
],
"pose": [
 ("pov", r"\b(pov|point of view|first person|male pov|female pov|from viewer)\b"),
 ("selfie", r"\b(selfie|mirror selfie|phone camera|front camera)\b"),
 ("from behind", r"\b(from behind|rear view|back view|behind view|looking back|over the shoulder)\b"),
 ("from below", r"\b(from below|low angle|worm.?s eye|looking up at)\b"),
 ("from above", r"\b(from above|high angle|bird.?s eye|top down|overhead|looking down)\b"),
 ("from side", r"\b(from side|side view|profile)\b"),
 ("close-up", r"\b(close ?up|closeup|macro|extreme close|detail shot|face focus|zoom in)\b"),
 ("full body", r"\b(full ?body|full shot|wide shot|long shot|head to toe)\b"),
 ("portrait", r"\b(portrait|headshot|upper body|bust shot|cowboy shot)\b"),
 ("cross-section", r"\b(cross ?section|x ?ray|internal view|cutaway|inside view)\b"),
 ("multiple views", r"\b(multiple views|multi ?view|split screen|before and after|comparison|collage|panel\w*|grid)\b"),
 ("dutch angle", r"\b(dutch angle|tilted|canted)\b"),
 ("fisheye", r"\b(fish ?eye|wide angle|ultra wide)\b"),
 ("standing", r"\b(standing|stand)\b"),
 ("sitting", r"\b(sitting|seated|sit)\b"),
 ("lying", r"\b(lying|laying|on back|on stomach|reclining|on bed)\b"),
 ("kneeling", r"\b(kneel\w*|on knees|on her knees)\b"),
 ("squatting", r"\b(squat\w*|crouch\w*)\b"),
 ("all fours", r"\b(all fours|hands and knees|on all fours)\b"),
 ("bent over", r"\b(bent over|bending over|bend over|leaning forward|top down bottom up|jack o)\b"),
 ("spread legs", r"\b(spread\w*|legs apart|spread legs|spread pussy|spread ass|m legs|split\w*)\b"),
 ("legs up", r"\b(legs up|legs over head|feet up|leg lift|leg up|legs in air)\b"),
 ("arms up", r"\b(arms? up|arms behind head|hands behind head|armpits?|stretching)\b"),
 ("hand on hip", r"\b(hand on hip|hands on hips|contrapposto|model pose|posing|pose)\b"),
 ("walking", r"\b(walking|walk|strut\w*|running|run)\b"),
 ("dancing", r"\b(danc\w*|twerk\w*|pole dance|belly dance|grinding)\b"),
 ("hugging", r"\b(hug|hugs|hugging|hugged|embrac\w*|cuddl\w*|holding hands|carrying|carried|princess carry)\b"),
 ("missionary", r"\b(missionary|mating press|legs on shoulders)\b"),
 ("cowgirl", r"\b(cowgirl|reverse cowgirl|riding|straddling|girl on top|woman on top)\b"),
 ("doggystyle", r"\b(doggy\w*|from behind sex|prone bone|prone|bent over sex)\b"),
 ("standing sex", r"\b(standing sex|against wall|lift and carry|full nelson|suspended congress|standing split)\b"),
 ("spooning", r"\b(spooning|side ?ways sex|lying on side)\b"),
 ("69", r"\b(69|sixty ?nine)\b"),
 ("face sitting", r"\b(face ?sit\w*|queening|smother\w*)\b"),
 ("piledriver", r"\b(piledriver|pile driver|amazon position)\b"),
 ("presenting", r"\b(present\w*|showing off|displaying|flaunt\w*|spread ass|ass up)\b"),
 ("grabbing", r"\b(grab\w*|groping|grope|squeez\w*|holding breasts|breast grab|ass grab|hand on)\b"),
 ("action", r"\b(action|fighting|combat|attack\w*|jump\w*|flying|kick\w*|punch\w*|swing\w*)\b"),
],
"style": [
 ("photoreal", r"\b(photo\w*|realistic|realism|real life|live action|raw photo|dslr|lifelike|hyperreal\w*|photograph\w*|35mm|film photo)\b"),
 ("amateur", r"\b(amateur|candid|snapshot|phone (photo|snap)|iphone|instagram|selfie|homemade|onlyfans|flash photo|point and shoot|digicam|webcam|unpolished|casual)\b"),
 ("cinematic", r"\b(cinematic|film still|movie still|movie scene|anamorphic|film grain|kodak|cinestill|technicolor|widescreen|letterbox)\b"),
 ("vintage retro", r"\b(vintage|retro|[1-9]0s|\d{4}s|old school|polaroid|vhs|y2k|nostalgi\w*|analog|80s|90s|70s|60s|50s|sepia|pin ?up)\b"),
 ("anime", r"\b(anime|manga|2d|cel shad\w*|japanese animation|anime style|anime screencap|danbooru|waifu|chibi|moe)\b"),
 ("retro anime", r"\b(retro anime|90s anime|80s anime|old anime|ova|showa)\b"),
 ("comic", r"\b(comic\w*|western comic|graphic novel|halftone|screentone\w*|ink\w*|lineart|line art|bold lines?|doujin\w*|manhwa|webtoon\w*|panel)\b"),
 ("cartoon", r"\b(cartoon\w*|toon|western animation|disney style|pixar style|flat colou?r|vector|simpsons style)\b"),
 ("3d", r"\b(3d|cgi|cg|render\w*|blender|unreal engine|octane|source filmmaker|sfm|daz|koikatsu|honey select|video game|game art|clay|claymation|figure|figurine|pvc figure)\b"),
 ("painting", r"\b(paint\w*|oil paint\w*|acrylic|watercolou?r|gouache|impasto|brush strokes?|canvas|fine art|classical art|renaissance|baroque|impressionis\w*)\b"),
 ("sketch", r"\b(sketch\w*|pencil|graphite|charcoal|drawing|doodle|line drawing|monochrome|greyscale|grayscale|black and white|b&w)\b"),
 ("pixel art", r"\b(pixel\w*|8 ?bit|16 ?bit|sprite)\b"),
 ("artist style", r"\b(artist|art style|artstyle|style of|in the style|style lora|by [a-z]+style|illustrator|mangaka)\b"),
 ("illustration", r"\b(illustration|digital art|concept art|semi ?realistic|semi real|2\.5d|painterly)\b"),
 ("dark gothic", r"\b(dark|gothic|goth|grim|noir|horror|creepy|moody|shadowy)\b"),
 ("neon cyberpunk", r"\b(neon|cyberpunk|synthwave|vaporwave|outrun|retrowave|glitch)\b"),
 ("fantasy art", r"\b(fantasy art|dnd|d&d|magic the gathering|mtg|tarot|card art|epic fantasy)\b"),
 ("ukiyo-e", r"\b(ukiyo ?e|woodblock|sumi ?e|chinese ink|shan shui|traditional japanese)\b"),
 ("art nouveau", r"\b(art nouveau|mucha|art deco|stained glass)\b"),
 ("pastel soft", r"\b(pastel|soft (colou?rs|light)|dreamy|ethereal|airy|kawaii)\b"),
 ("high contrast", r"\b(high contrast|bold colou?rs?|vivid|saturated|chiaroscuro|dramatic lighting)\b"),
 ("glamour", r"\b(glamou?r|boudoir|fashion|editorial|studio shot|magazine|playboy|penthouse|pin ?up|centerfold|beauty shot)\b"),
 ("surreal", r"\b(surreal\w*|dreamlike|abstract|psychedelic|trippy|weird|liminal)\b"),
 ("hentai", r"\b(hentai|ecchi|eroge|h manga|doujinshi|nsfw anime)\b"),
],
"anatomy": [
 ("breasts", r"\b(breast\w*|boob\w*|tits?|titties|bust|cleavage|chest|oppai|underboob|sideboob)\b"),
 ("nipples", r"\b(nipple\w*|areola\w*|puffy nipples|inverted nipples)\b"),
 ("huge breasts", r"\b(huge breasts|gigantic breasts|large breasts|big (boobs|breasts|tits)|massive breasts|hyper breasts|busty)\b"),
 ("small breasts", r"\b(small breasts|flat chest|tiny breasts|perky breasts|a ?cup)\b"),
 ("penis", r"\b(penis|penises|cock\w*|dick\w*|phallus|erection|shaft|glans|foreskin|uncut|circumcised|micropenis|flaccid|bulge)\b"),
 ("testicles", r"\b(testicle\w*|balls|scrotum|ballsack|nutsack)\b"),
 ("vulva", r"\b(pussy|vulva|vagina\w*|labia|clit\w*|cameltoe|camel toe|mons|cervix|spread pussy|innie|outie)\b"),
 ("anus", r"\b(anus|asshole|anal|rosebud|prolapse|gape|gaping)\b"),
 ("ass", r"\b(ass|butt\w*|buttocks|booty|glutes|rear|bum|thicc|bubble butt|cheeks)\b"),
 ("hips thighs", r"\b(hips?|thighs?|thick thighs|wide hips|thigh gap|legs|calves)\b"),
 ("belly navel", r"\b(belly|navel|stomach|tummy|abs|abdomen|waist|midriff|six pack)\b"),
 ("feet", r"\b(feet|foot|soles|toes|barefoot)\b"),
 ("hands", r"\b(hands?|fingers?|nails|manicure|fingernails)\b"),
 ("face", r"\b(face|facial features|lips|eyes|eyelashes|nose|freckles|makeup|teeth|tongue)\b"),
 ("hair", r"\b(hair\w*|ponytail|braid\w*|bangs|bob cut|twin ?tails|pigtails|bun|curly|afro|bald|haircut)\b"),
 ("pubic hair", r"\b(pubic\w*|bush|hairy pussy|trimmed|shaved|armpit hair|body hair|hairy)\b"),
 ("skin", r"\b(skin|tan|tanned|tanning|suntan\w*|tan ?lines?|freckle\w*|moles?|stretch marks?|cellulite|pores|veins?|scars?|tattoo\w*|body paint|wrinkles|sunburn|goosebumps)\b"),
 ("body type", r"\b(body type|curvy|hourglass|thick|chubby|slim|skinny|fit|muscular|athletic|petite|bbw|plump|voluptuous|body shape|physique)\b"),
 ("muscle", r"\b(muscle\w*|muscular|abs|biceps|six pack|ripped|toned)\b"),
 ("internal anatomy", r"\b(cross ?section|x ?ray|internal|uterus|womb|cervix|prostate|urethra|colon|pelvi\w*|rectum|intestine|bladder|anatomy|anatomical)\b"),
 ("fluids", r"\b(cum|semen|saliva|drool\w*|sweat|pussy juice|squirt|lactation|milk|wetness|precum|spit)\b"),
 ("pregnant belly", r"\b(pregnant|pregnancy|baby bump|belly bulge|stomach bulge|inflation)\b"),
 ("tongue", r"\b(tongue\w*|long tongue|tongue out|licking)\b"),
 ("armpits", r"\b(armpit\w*|underarm)\b"),
 ("eyes", r"\b(eyes|heterochromia|pupils|iris|eye colou?r|glowing eyes)\b"),
],
"motion": [
 ("thrusting", r"\b(thrust\w*|pump\w*|pounding|humping|fucking motion|hip movement)\b"),
 ("bouncing", r"\b(bounc\w*|jiggl\w*|jiggle|wobble|sway\w*|breast physics|body physics|ass shake|twerk\w*|physics)\b"),
 ("riding motion", r"\b(riding|grinding|cowgirl motion|hip roll)\b"),
 ("oral motion", r"\b(sucking|bobbing|head bob|licking|deepthroat\w*|gagging|throat)\b"),
 ("stroking motion", r"\b(stroking|jerking|handjob motion|rubbing|fingering)\b"),
 ("camera orbit", r"\b(orbit\w*|360|turntable|rotate|rotation|spin|spins|spinning|arc shot|bullet time|frozen time)\b"),
 ("camera push", r"\b(push ?in|zoom ?in|dolly ?in|crash zoom|zoom ?out|dolly ?out|pull back|dolly zoom|vertigo)\b"),
 ("camera pan", r"\b(pan|pans|panning|tilt|tilts|tilting|tracking shot|follow cam|crane|jib|drone|aerial|fly ?through|handheld|shaky cam|steadicam)\b"),
 ("static camera", r"\b(static camera|locked camera|tripod|locked off|fixed camera|still camera)\b"),
 ("slow motion", r"\b(slow ?mo\w*|slow motion|time ?lapse|hyperlapse|speed ramp)\b"),
 ("walking motion", r"\b(walk\w*|run\w*|strut\w*|catwalk|stride)\b"),
 ("dance motion", r"\b(danc\w*|choreograph\w*|twerk\w*|pole dance)\b"),
 ("talking motion", r"\b(talk\w*|lip ?sync|speech|speaking|voice|singing|moan\w*|vocal\w*|audio|sound)\b"),
 ("facial motion", r"\b(facial (motion|animation)|expression change|blink\w*|wink\w*|smile animation)\b"),
 ("undressing motion", r"\b(undress\w*|strip|stripping|striptease|stripper|taking off|removing (clothes|bra|panties)|getting dressed)\b"),
 ("cumshot motion", r"\b(cumshot|ejaculat\w*|cum ?shot|squirting|cum spurt|creampie reveal)\b"),
 ("transition", r"\b(transition\w*|morph\w*|transform\w*|metamorph\w*|cut to|match cut)\b"),
 ("vfx", r"\b(vfx|explosion\w*|fire|smoke|particles|magic effect|lightning|energy|disintegrat\w*|liquid|splash|water effect)\b"),
 ("character consistency", r"\b(consisten\w*|identity|keep face|face lock|reference|character swap|face swap|head swap)\b"),
 ("motion quality", r"\b(smooth motion|less morph\w*|motion quality|realistic motion|natural motion|anti ?jitter|stabil\w*|loop\w*|seamless loop)\b"),
],
}

COMPILED = {c: [(t, re.compile(rx, re.I)) for t, rx in pats] for c, pats in L.items()}

def norm_text(s: str) -> str:
    s = (s or "")
    s = re.sub(r"<[^>]*>", " ", s)  # strip html and <lora:...> blocks
    s = s.replace("_", " ").replace("-", " ")
    return s.lower()

def tag_text(*parts, categories=None) -> dict:
    """Return {category: [tags]} for the given text parts (weights: earlier parts count first)."""
    text = norm_text(" | ".join(p for p in parts if p))
    out = {}
    for c in (categories or CATEGORIES):
        hits = [t for t, rx in COMPILED[c] if rx.search(text)]
        if hits:
            out[c] = hits
    return out

# -------- safety --------
# Hard exclusions (never catalogued): explicit loli/shota/underage terms in a LoRA's own name, triggers or tags, and the
# forbidden real-person identities. Everything else that is minor-coded is KEPT and flagged `minor_coded` (see minor_flag);
# suggest.py never offers flagged LoRAs for NSFW prompts and never stacks them with NSFW or anatomy LoRAs.
HARD_RE = re.compile(r"\b(loli\w*|shota\w*|toddler|underage|under ?age|preteen|pre ?teen)\b", re.I)
FORBIDDEN_ID_RE = re.compile(r"youngandrew|handyandy|andrewyoung|andy\.?young", re.I)

def blocked(*texts) -> str | None:
    """Hard exclusion reason for name/trigger/tag text, else None."""
    for t in texts:
        if not t:
            continue
        t2 = norm_text(t)
        if FORBIDDEN_ID_RE.search(t2):
            return "forbidden identity"
        m = HARD_RE.search(t2)
        if m:
            return f"explicit minor term in name/tags: {m.group(0)}"
    return None

# -------- tokens for lexical matching --------
STOP = set("""a an the and or of in on at to for with by from as is are be it its this that these those his her their your my our
lora loras lycoris locon dora model models version ver v v1 v2 v3 v4 v5 v6 v10 final epoch step steps xl sdxl ill illustrious noob noobai
pony anima krea krea2 moss h3 wan ltx ltx2 wan21 wan22 i2v t2v 14b 5b high low noise concept style character trigger weight
strength best quality masterpiece score 9 8 7 up 8k 4k hd high res detailed very newest absurdres highres safe nsfw sfw explicit
sensitive general rating solo one 1 2 3 4 5 6 into onto over under not no
doing does do did very just make makes making get gets some while then there here has have having like""".split())

TOKEN_RE = re.compile(r"[a-z0-9\u3040-\u30ff\u4e00-\u9fff]+")

def tokens(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(norm_text(text)) if t not in STOP and len(t) > 1 and not t.isdigit()]

def bigrams(toks: list[str]) -> list[str]:
    return [f"{a} {b}" for a, b in zip(toks, toks[1:])]

FAMILY_SUFFIX_RE = re.compile(r"-(anima|ill|il|xl|krea2?|moss|pony|sdxl|h3|wan|ltx2?|flux|zit|zimage|qwen|chroma)(-\d+)?$")

def weight_from_text(desc: str):
    """Source-stated weight/strength in a description, else None. Never invents."""
    if not desc:
        return None
    m = re.search(r"(?:recommended\s+)?(?:weight|strength|lora strength|lora weight)s?\s*[:=：]?\s*(?:of\s+|around\s+|about\s+|~)?(-?[0-9](?:\.[0-9]+)?(?:\s*(?:-|–|~|to)\s*-?[0-9](?:\.[0-9]+)?)?)", desc, re.I)
    if m:
        v = m.group(1).strip()
        try:
            nums = [float(x) for x in re.findall(r"-?[0-9](?:\.[0-9]+)?", v)]
            if all(-3 <= n <= 3 for n in nums):
                return v.replace(" ", "")
        except Exception:
            return None
    return None

# Specific characters that are canonically under 18 or school-age/students (named individually; no franchise rules).
# Kept in the catalogs for SFW use and flagged `minor_coded`.
MINOR_CHARACTER_RE = re.compile(r"\b(asuka langley|souryuu|soryu|rei ayanami|ayanami rei|shinji|mari makinami|lillie|nemona|iono|fern frieren|frieren fern|fern sousou|marin kitagawa|rias gremory|akeno|koneko|asia argento|xenovia|nezuko|kanao|mikasa|annie leonhart|historia reiss|sasha braus|hinata hyuga|hinata hyuuga|sakura haruno|ino yamanaka|tenten|temari|uraraka|ochako|himiko toga|toga himiko|momo yaoyorozu|kyoka jirou|jirou kyouka|tsuyu asui|mina ashido|nobara|maki zenin|makima young|anya forger|ruby hoshino|kana arima|akane kurokawa|chisato nishikigi|takina inoue|megumin|ram rezero|rem rezero|zero two|ichigo franxx|ryuko matoi|satsuki kiryuin|mako mankanshoku|nui harime|yuffie|katara|toph|azula|ty lee|mai avatar|zelda (oot|ocarina|skyward|botw|totk)|raven teen titans|starfire teen titans|teen titans starfire|jinx teen titans|serial experiments lain|lain iwakura|meg griffin|summer smith|daphne blake|velma|courtney total drama|gwen tennyson|kim possible|violet parr|sam manson|star butterfly|marco diaz|luz noceda|amity blight|anne boonchuy|marcy wu|sasha waybright|tinker ?bell|civchan|bulma (og|young|teen|dragon ball original)|tron bonne|kirara onizaki|sophie neuenmuller|ryza|reisalin|usagi tsukino|ami mizuno|rei hino|makoto kino|minako aino|aino minako|chibiusa|madoka kaname|homura akemi|sayaka miki|kyoko sakura|mami tomoe|nagisa momoe|haruhi suzumiya|mikuru|yuki nagato|hatsune miku|kagamine|rin tohsaka|sakura matou|illyasviel|illya|chloe von|miyu edelfelt|klee|qiqi|nahida|sayu|diona|yaoyao|bailu|hook honkai|bronya zaychik|kiana kaslana|chika fujiwara|kaguya shinomiya|ai hayasaka|komi shouko|power chainsaw young|shiroko|hoshino blue|aru blue|mika misono|hina sorasaki|yuuka hayase|asuna ichinose|nonomi|serika kuromi|hifumi ajima|azusa shirasu|hanako urawa)\b", re.I)
AGE_RE = re.compile(r"\b(age ?slider|age ?(adjust\w*|tweak\w*|changer|control)|aging slider|de ?ag(e|ed|ing)|younger (version|self|look\w*)|age ?regress\w*|reverse aging|rejuvenat\w*)\b", re.I)
EXPLICIT_NAME_RE = re.compile(r"\b(child|children|kids?|minor|minors|underage)\b", re.I)
EXPLICIT_DESC_RE = re.compile(r"\b(loli\w*|shota\w*|child|children|underage|preteen)\b", re.I)

POKEMON_KID_RE = re.compile(r"\b(misty|dawn|serena|may|iris|bonnie|lana|mallow|lillie|gloria|marnie|nemona|juliana|penny|ash ketchum|hilda|rosa|selene)\W+(\w+\W+)?pok[eé]mon|pok[eé]mon\W+(\w+\W+)?(misty|dawn|serena|may|iris|bonnie|lana|mallow|lillie|gloria|marnie|nemona|juliana|penny|ash ketchum|hilda|rosa|selene)\b", re.I)

def minor_flag(name_texts, desc: str = "") -> str | None:
    """Reason to flag an entry minor_coded (kept, SFW-only in suggest.py), else None."""
    t = norm_text(" | ".join(x for x in name_texts if x))
    m = MINOR_CHARACTER_RE.search(t) or POKEMON_KID_RE.search(t)
    if m:
        return f"canonically minor/school-age character: {m.group(0)}"
    m = AGE_RE.search(t)
    if m:
        return f"age slider / de-aging: {m.group(0)}"
    m = EXPLICIT_NAME_RE.search(t)
    if m:
        return f"name/tags say: {m.group(0)}"
    m = re.search(r"\blolita\b", t)
    if m:
        return "lolita (fashion term, but ambiguous: SFW only)"
    m = EXPLICIT_DESC_RE.search(norm_text(desc or "")[:800])
    if m:
        return f"description says: {m.group(0)}"
    return None

NSFW_CONCEPTS = {"sex", "oral", "anal", "handjob", "titjob", "footjob", "masturbation", "cumshot", "squirt", "orgasm", "bdsm",
                 "groupsex", "lesbian", "gay", "nudity", "exhibitionism", "toys", "condom", "chastity", "lactation", "watersports",
                 "worship", "humiliation", "aftermath", "tentacles"}
NSFW_ANATOMY = {"nipples", "penis", "testicles", "vulva", "anus", "pubic hair", "fluids"}
NSFW_POSE = {"missionary", "cowgirl", "doggystyle", "standing sex", "spooning", "69", "face sitting", "piledriver"}
NSFW_WORDS = re.compile(r"\b(nsfw|explicit|nude|naked|nudity|topless|bottomless|porn\w*|hentai|sex|sexual|xxx|erotic|lewd|uncensored|fuck\w*|cum\w*|pussy|penis|cock|dick|nipples?|vagina|vulva|anus|orgasm|masturbat\w*|blowjob|fellatio|cunnilingus|creampie|bukkake|bdsm|bondage)\b", re.I)

def is_nsfw(sem: dict, text: str = "") -> bool:
    return bool(set(sem.get("concept", [])) & NSFW_CONCEPTS or set(sem.get("anatomy", [])) & NSFW_ANATOMY
                or set(sem.get("pose", [])) & NSFW_POSE or NSFW_WORDS.search(norm_text(text)))
