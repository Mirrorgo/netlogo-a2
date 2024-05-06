breed [ agents an-agent ]
breed [ cops cop ]

globals [
  k                   ; factor for determining arrest probability
  threshold           ; by how much must G > N to make someone rebel?
]

agents-own [
  risk-aversion       ; R, fixed for the agent's lifetime, ranging from 0-1 (inclusive)
  perceived-hardship  ; H, also ranging from 0-1 (inclusive)
  active?             ; if true, then the agent is actively rebelling
  jail-term           ; how many turns in jail remain? (if 0, the agent is not in jail)
]

patches-own [
  neighborhood        ; surrounding patches within the vision radius
]

to setup
  clear-all

  ; set globals
  set k 2.3
  set threshold 0.1

  ask patches [
    ; make background a slightly dark gray
    set pcolor gray - 1
    ; cache patch neighborhoods
    set neighborhood patches in-radius vision
  ]

  if initial-cop-density + initial-agent-density > 100 [
    user-message (word
      "The sum of INITIAL-COP-DENSITY and INITIAL-AGENT-DENSITY "
      "should not be greater than 100.")
    stop
  ]

  ; create cops
  create-cops round (initial-cop-density * .01 * count patches) [
    move-to one-of patches with [ not any? turtles-here ]
    display-cop
  ]

  ; create agents
  create-agents round (initial-agent-density * .01 * count patches) [
    move-to one-of patches with [ not any? turtles-here ]
    set heading 0
    set risk-aversion random-float 1.0
    set perceived-hardship random-float 1.0
    set active? false
    set jail-term 0
    display-agent
  ]

  ; start clock and plot initial state of system
  reset-ticks
end

to go
  ask turtles [
    ; Rule M: Move to a random site within your vision
    if (breed = agents and jail-term = 0) or breed = cops [ move ]
    ;   Rule A: Determine if each agent should be active or quiet
    if breed = agents and jail-term = 0 [ determine-behavior ]
    ;  Rule C: Cops arrest a random active agent within their radius
    if breed = cops [ enforce ]
  ]
  ; Jailed agents get their term reduced at the end of each clock tick
  ask agents [ if jail-term > 0 [ set jail-term jail-term - 1 ] ]
  ; update agent display
  ask agents [ display-agent ]
  ask cops [ display-cop ]
  ; advance clock and update plots
  tick
end

; AGENT AND COP BEHAVIOR

; move to an empty patch
to move ; turtle procedure
  if movement? or breed = cops [
    ; move to a patch in vision; candidate patches are
    ; empty or contain only jailed agents
    let targets neighborhood with [
      not any? cops-here and all? agents-here [ jail-term > 0 ]
    ]
    if any? targets [ move-to one-of targets ]
  ]
end

; AGENT BEHAVIOR

to determine-behavior
  set active? (grievance - risk-aversion * estimated-arrest-probability > threshold)
end

to-report grievance
  report perceived-hardship * (1 - government-legitimacy)
end

to-report estimated-arrest-probability
  let c count cops-on neighborhood
  let a 1 + count (agents-on neighborhood) with [ active? ]
  ; See Info tab for a discussion of the following formula
  report 1 - exp (- k * floor (c / a))
end

; COP BEHAVIOR

to enforce
  if any? (agents-on neighborhood) with [ active? ] [
    ; arrest suspect
    let suspect one-of (agents-on neighborhood) with [ active? ]
    move-to suspect  ; move to patch of the jailed agent
    ask suspect [
      set active? false
      set jail-term random max-jail-term
    ]
  ]
end

; VISUALIZATION OF AGENTS AND COPS

to display-agent  ; agent procedure
  ifelse visualization = "2D"
    [ display-agent-2d ]
    [ display-agent-3d ]
end

to display-agent-2d  ; agent procedure
  set shape "circle"
  ifelse active?
    [ set color red ]
    [ ifelse jail-term > 0
        [ set color black + 3 ]
        [ set color scale-color green grievance 1.5 -0.5 ] ]
end

to display-agent-3d  ; agent procedure
  set color scale-color green grievance 1.5 -0.5
  ifelse active?
    [ set shape "person active" ]
    [ ifelse jail-term > 0
        [ set shape "person jailed" ]
        [ set shape "person quiet" ] ]
end

to display-cop
  set color cyan
  ifelse visualization = "2D"
    [ set shape "triangle" ]
    [ set shape "person soldier" ]
end


; Copyright 2004 Uri Wilensky.
; See Info tab for full copyright and license.