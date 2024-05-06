globals
[
  row           ;; current row
  old-rule      ;; previous rule
  rules-shown?  ;; flag to check if rules have been displayed
  gone?         ;; flag to check if go has already been pressed
]

patches-own
[on?]

to startup  ;; initially, nothing has been displayed
  set rules-shown? false
  set gone? false
  set old-rule rule
end

;;;;;;;;;;;;;;;;;;;;;;;;
;;; Setup Procedures ;;;
;;;;;;;;;;;;;;;;;;;;;;;;

to setup-general  ;; setup general working environment
  clear-patches
  clear-turtles
  set row max-pycor   ;; reset current row
  refresh-rules
  set gone? false
  set rules-shown? false  ;; rules are no longer shown since the view has been cleared
end

to single-cell
  setup-general
  reset-ticks
  ask patches with [pycor = row] [set on? false set pcolor background]  ;; initialize top row
  ask patch 0 row [ set pcolor foreground ]  ;; setup single cell in top center
  ask patch 0 row [ set on? true ]
end

to setup-random
  setup-general
  reset-ticks
  ask patches with [pycor = row]  ;; randomly place cells across the top of the world
  [
    set on? ((random-float 100) < density)
    color-patch
  ]
end

to setup-random1
  setup-general
  reset-ticks
  ask patches with [pycor = row]  ;; 设置顶部单元格的状态
  [
    ;; 根据 pxcor（横坐标）确定奇偶性，并设置相应的状态
    ifelse is-odd? pxcor [
      set on? true  ;; 如果是奇数格子，则填充
    ] [
      set on? false  ;; 如果是偶数格子，则为空
    ]
    color-patch
  ]
end

to-report is-odd? [n]  ;; 判断是否为奇数的函数
  report n mod 2 != 0
end


to setup-continue
  let on?-list []
  if not gone?  ;; make sure go has already been called
    [ stop ]
  ;; copy cell states from the current row to a list
  set on?-list map [ p -> [ on? ] of p ] sort patches with [ pycor = row ]
  setup-general
  ask patches with [ pycor = row ]
  [
    set on? item (pxcor + max-pxcor) on?-list  ;; copy states from list to top row
    color-patch
  ]
end


;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; GO Procedures      ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;

to go
  if (rules-shown?)  ;; don't do unless we are properly set up
    [ stop ]
  if (row = min-pycor)  ;; if we reach the end, continue from the top or stop
  [
    ifelse auto-continue?
    [
        set gone? true
        display    ;; ensure everything gets drawn before we clear it
        setup-continue
    ]
    [
      ifelse gone?
        [ setup-continue ]       ;; a run has already been completed, so continue with another
        [ set gone? true stop ]  ;; otherwise just stop
    ]
  ]
  ask patches with [ pycor = row ]  ;; apply rule
    [ do-rule ]
  set row (row - 1)
  ask patches with [ pycor = row ]  ;; color in changed cells
    [ color-patch ]
  tick
end


to do-rule  ;; patch procedure
  let left-on? [on?] of patch-at -1 0  ;; set to true if the patch to the left is on
  let right-on? [on?] of patch-at 1 0  ;; set to true if the patch to the right is on

  ;; each of these lines checks the local area and (possibly)
  ;; sets the lower cell according to the corresponding switch
  let new-value
    (iii and left-on?       and on?       and right-on?)          or
    (iio and left-on?       and on?       and (not right-on?))    or
    (ioi and left-on?       and (not on?) and right-on?)          or
    (ioo and left-on?       and (not on?) and (not right-on?))    or
    (oii and (not left-on?) and on?       and right-on?)          or
    (oio and (not left-on?) and on?       and (not right-on?))    or
    (ooi and (not left-on?) and (not on?) and right-on?)          or
    (ooo and (not left-on?) and (not on?) and (not right-on?))
  ask patch-at 0 -1 [ set on? new-value ]
end


;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Utility Procedures ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;

to color-patch  ;;patch procedure
  ifelse on?
    [ set pcolor foreground ]
    [ set pcolor background ]
end


to-report bindigit [number power-of-two]
  ifelse (power-of-two = 0)
    [ report floor number mod 2 ]
    [ report bindigit (floor number / 2) (power-of-two - 1) ]
end

to refresh-rules  ;; update either switches or slider depending on which has been changed last
  ifelse (rule = old-rule)
  [
    if (rule != calculate-rule)
      [ set rule calculate-rule ]
  ]
  [ extrapolate-switches ]
  set old-rule rule
end

to extrapolate-switches
  ;; set the switches based on the slider
  set ooo ((bindigit rule 0) = 1)
  set ooi ((bindigit rule 1) = 1)
  set oio ((bindigit rule 2) = 1)
  set oii ((bindigit rule 3) = 1)
  set ioo ((bindigit rule 4) = 1)
  set ioi ((bindigit rule 5) = 1)
  set iio ((bindigit rule 6) = 1)
  set iii ((bindigit rule 7) = 1)
end

to-report calculate-rule
  ;; set the slider based on the switches
  let result 0
  if ooo [ set result result +   1 ]
  if ooi [ set result result +   2 ]
  if oio [ set result result +   4 ]
  if oii [ set result result +   8 ]
  if ioo [ set result result +  16 ]
  if ioi [ set result result +  32 ]
  if iio [ set result result +  64 ]
  if iii [ set result result + 128 ]
  report result
end


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; SHOW-RULES RELATED PROCEDURES ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

to show-rules  ;; preview cell state transitions
  setup-general
  ask patches with [pycor > max-pycor - 12]
    [ set pcolor gray - 1 ]
  let i 0
  foreach list-rules [ the-rule ->
    let px (min-pxcor + i * floor (world-width / 8) + floor (world-width / 16)) - 4
    ask patch px (max-pycor - 4)
    [
      sprout 1
      [
        set xcor xcor - 3
        print-block item 0 the-rule  ;; left cell
        set xcor xcor + 3
        print-block item 1 the-rule  ;; center cell
        set xcor xcor + 3
        print-block item 2 the-rule  ;; right cell
        setxy (xcor - 3) (ycor - 3)
        print-block item 3 the-rule  ;; next cell state
        die
      ]
    ]
    set i (i + 1)
  ]
  set rules-shown? true
end

;; turtle procedure
to print-block [print-on?]  ;; draw a 3x3 block with the color determined by the state
  ask patches in-radius 1.5  ;; like "neighbors", but includes the patch we're on too
  [
    set on? print-on?
    color-patch
  ]
end

to-report list-rules  ;; return a list of state-transition 4-tuples corresponding to the switches
  report (list lput ooo [false false false]
               lput ooi [false false true ]
               lput oio [false true  false]
               lput oii [false true  true ]
               lput ioo [true  false false]
               lput ioi [true  false true ]
               lput iio [true  true  false]
               lput iii [true  true  true ])
end


; Copyright 1998 Uri Wilensky.
; See Info tab for full copyright and license.