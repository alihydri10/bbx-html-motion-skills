# Motion direction

A scroll cinema works when it feels directed: every stage has one move, one change, one idea. These
are the rules that get it there.

## Camera grammar

| Stage job | Shot | Camera | Typical move |
|-----------|------|--------|--------------|
| Establish the place | wide, high | 150–250 units out, 35–45° down | slow drift, almost static |
| Introduce a machine or step | medium | 25–40 units from the object, eye slightly above | push in from the previous wide |
| Show a process working | medium-close | 15–25 units, a three-quarter angle | small lateral slide while the scene animates |
| Evidence, mechanism, "inside" | close | inside a close-up set, low, near the surface | fade cut in, slow creep |
| Payoff | wide again | the establishing position, slightly higher | pull back, everything changed |

Two consecutive stages should not use the same shot size unless the second is a deliberate hold.
Alternate wide and close the way an edit does.

## One change per stage

The scene state (`scene:{...}`) should change in one visible way per stage: ground darkens, bands
light up, plants rise, a flow switches on. If two things change at once, the reader cannot tell what
the stage was about. Let `uTime` keep small life in the hold (pulses, drifting particles) so the frame
never freezes.

## Pacing

- Opening: 3 to 5 seconds of autoplay, about 5% of scroll.
- Each stage: 9 to 13 seconds of autoplay. The arrive/leave split (30% move, 58% hold, 12% leave)
  gives roughly 3 s of motion and 6 s of reading.
- Total under 2.5 minutes. Past that, split into sections (Section A, B, C) with a handoff line at
  the end of each, which is how long stories stay watchable.

## Easing

Everything is smoothstepped between keys, so moves start and stop softly. Do not add springs or
overshoot to the camera; overshoot reads as a mistake in a slow film. Card and panel fades are 0.5 s
with a 12 px rise, which matches the scroll feel. Labels fade in 0.3 s.

## Text against image

- The headline sits on the left third, over a veil gradient; keep the camera's subject in the right
  two thirds at the opening.
- At each stage, frame the subject in the upper two thirds so the HUD row never covers it.
- Cards hold one paragraph. If a stage needs numbers, they go in the panel, and the card says what
  the numbers mean in words.

## Handoffs between sections

End each section on the wide payoff and a line naming what the next section covers. Start the next
section on the same wide shot so a reader moving between pages feels one continuous film.

## Making a still deck feel like scroll

When the same story must also exist as slides (meetings, PDF), keep the motion vocabulary: a
persistent progress rail whose marker moves between slides (magic-move transitions with a shared
element id), content that rises in on each slide, dark story slides with light "lab report" slides for
data, and the same stage numbering (B01, B02 ...). The deck then reads as the film's storyboard.
