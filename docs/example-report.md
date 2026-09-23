<!--
Sample output — committed on purpose (unlike the per-user report.md, which is git-ignored).
Produced by `python3 generate.py` (no layers) from the bundled `source/default.xml` —
the stock IntelliJ `$default` keymap. Regenerate with:  cp report.md docs/example-report.md
-->

# IntelliKeyPort - keymap port report (IntelliJ -> VS Code)

- source file: `source/default.xml`
- source actions parsed: **485**
- generated entries: **141**
- curated layers: `overrides.jsonc`
- curated entries: **4**
- total in keybindings.generated.json: **145**

## Key conflicts - resolved by keymap order (earlier action wins)  (1)

```
ctrl+e   keep workbench.action.openRecent   drop workbench.action.openPreviousEditorFromHistory
```

## Key conflicts - no winner picked (resolve in a layer)  (0)

_none_

## Key conflicts - a curated layer picks the winner  (0)

_none_

## Mapped -> emitted  (142)

```
acceptAlternativeSelectedSuggestion  <-  tab  (EditorChooseLookupItemReplace)
acceptSelectedSuggestion  <-  ctrl+shift+enter  (EditorCompleteStatement)
breadcrumbs.focus  <-  alt+home  (ShowNavBar)
copyFilePath  <-  ctrl+shift+c  (CopyPaths)
cursorBottom  <-  ctrl+end  (EditorTextEnd)
cursorBottom  <-  ctrl+pagedown  (EditorMoveToPageBottom)
cursorBottomSelect  <-  ctrl+shift+pagedown  (EditorMoveToPageBottomWithSelection)
cursorLineEnd  <-  end  (EditorLineEnd)
cursorLineEndSelect  <-  shift+end  (EditorLineEndWithSelection)
cursorLineStart  <-  home  (EditorLineStart)
cursorLineStartSelect  <-  shift+home  (EditorLineStartWithSelection)
cursorTop  <-  ctrl+home  (EditorTextStart)
cursorTop  <-  ctrl+pageup  (EditorMoveToPageTop)
cursorTopSelect  <-  ctrl+shift+pageup  (EditorMoveToPageTopWithSelection)
cursorUndo  <-  shift+alt+j  (UnselectPreviousOccurrence)
cursorWordLeft  <-  ctrl+left  (EditorPreviousWord)
cursorWordLeftSelect  <-  ctrl+shift+left  (EditorPreviousWordWithSelection)
cursorWordRight  <-  ctrl+right  (EditorNextWord)
cursorWordRightSelect  <-  ctrl+shift+right  (EditorNextWordWithSelection)
deleteWordLeft  <-  ctrl+backspace  (EditorDeleteToWordStart)
deleteWordRight  <-  ctrl+delete  (EditorDeleteToWordEnd)
editor.action.addSelectionToNextFindMatch  <-  alt+j  (SelectNextOccurrence)
editor.action.blockComment  <-  ctrl+shift+/  (CommentByBlockComment)
editor.action.blockComment  <-  ctrl+shift+numpad_divide  (CommentByBlockComment)
editor.action.clipboardCopyAction  <-  ctrl+c  ($Copy)
editor.action.clipboardCopyAction  <-  ctrl+insert  ($Copy)
editor.action.clipboardCutAction  <-  ctrl+x  ($Cut)
editor.action.clipboardCutAction  <-  shift+delete  ($Cut)
editor.action.clipboardPasteAction  <-  ctrl+v  ($Paste)
editor.action.clipboardPasteAction  <-  shift+insert  ($Paste)
editor.action.codeAction  <-  ctrl+alt+m  (ExtractMethod)
editor.action.codeAction  <-  ctrl+alt+v  (IntroduceVariable)
editor.action.commentLine  <-  ctrl+/  (CommentByLineComment)
editor.action.commentLine  <-  ctrl+numpad_divide  (CommentByLineComment)
editor.action.copyLinesDownAction  <-  ctrl+d  (EditorDuplicate)
editor.action.deleteLines  <-  ctrl+y  (EditorDeleteLine)
editor.action.dirtydiff.next  <-  ctrl+shift+alt+down  (VcsShowNextChangeMarker)
editor.action.dirtydiff.previous  <-  ctrl+shift+alt+up  (VcsShowPrevChangeMarker)
editor.action.formatDocument  <-  ctrl+alt+l  (ReformatCode)
editor.action.goToImplementation  <-  ctrl+alt+b  (GotoImplementation)
editor.action.goToImplementation  <-  ctrl+u  (GotoSuperMethod)
editor.action.goToTypeDefinition  <-  ctrl+shift+b  (GotoTypeDeclaration)
editor.action.insertLineAfter  <-  shift+enter  (EditorStartNewLine)
editor.action.insertLineBefore  <-  ctrl+alt+enter  (EditorStartNewLineBefore)
editor.action.joinLines  <-  ctrl+shift+j  (EditorJoinLines)
editor.action.marker.next  <-  ctrl+alt+down  (NextOccurence)
editor.action.marker.prev  <-  ctrl+alt+up  (PreviousOccurence)
editor.action.moveLinesDownAction  <-  ctrl+shift+down  (MoveStatementDown)
editor.action.moveLinesDownAction  <-  shift+alt+down  (MoveLineDown)
editor.action.moveLinesUpAction  <-  ctrl+shift+up  (MoveStatementUp)
editor.action.moveLinesUpAction  <-  shift+alt+up  (MoveLineUp)
editor.action.nextMatchFindAction  <-  ctrl+l  (FindNext)
editor.action.nextSelectionMatchFindAction  <-  alt+down  (MethodDown)
editor.action.organizeImports  <-  ctrl+alt+o  (OptimizeImports)
editor.action.previewDeclaration  <-  ctrl+shift+i  (QuickImplementations)
editor.action.previousMatchFindAction  <-  ctrl+shift+l  (FindPrevious)
editor.action.previousSelectionMatchFindAction  <-  alt+up  (MethodUp)
editor.action.quickFix  <-  alt+enter  (ShowIntentionActions)
editor.action.referenceSearch.trigger  <-  ctrl+alt+f7  (ShowUsages)
editor.action.rename  <-  shift+f6  (RenameElement)
editor.action.revealDefinition  <-  ctrl+b  (GotoDeclaration)
editor.action.revealDefinition  <-  f4  (EditSource)
editor.action.selectAll  <-  ctrl+a  ($SelectAll)
editor.action.selectHighlights  <-  ctrl+shift+alt+j  (SelectAllOccurrences)
editor.action.showHover  <-  ctrl+q  (QuickJavaDoc)
editor.action.smartSelect.grow  <-  ctrl+w  (EditorSelectWord)
editor.action.smartSelect.shrink  <-  ctrl+shift+w  (EditorUnSelectWord)
editor.action.startFindReplaceAction  <-  ctrl+r  (Replace)
editor.action.toggleColumnSelection  <-  shift+alt+insert  (EditorToggleColumnMode)
editor.action.transformToUppercase  <-  ctrl+shift+u  (EditorToggleCase)
editor.action.triggerParameterHints  <-  ctrl+p  (ParameterInfo)
editor.debug.action.runToCursor  <-  alt+f9  (RunToCursor)
editor.debug.action.selectionToRepl  <-  alt+f8  (EvaluateExpression)
editor.debug.action.toggleBreakpoint  <-  ctrl+f8  (ToggleLineBreakpoint)
editor.fold  <-  ctrl+-  (CollapseRegion)
editor.fold  <-  ctrl+numpad_subtract  (CollapseRegion)
editor.foldAll  <-  ctrl+shift+-  (CollapseAllRegions)
editor.foldAll  <-  ctrl+shift+numpad_subtract  (CollapseAllRegions)
editor.unfold  <-  ctrl+=  (ExpandRegion)
editor.unfold  <-  ctrl+numpad_add  (ExpandRegion)
editor.unfoldAll  <-  ctrl+shift+=  (ExpandAllRegions)
editor.unfoldAll  <-  ctrl+shift+numpad_add  (ExpandAllRegions)
git.commitAll  <-  ctrl+k  (CheckinProject)
git.revertSelectedRanges  <-  ctrl+alt+z  (Vcs.RollbackChangedLines)
git.sync  <-  ctrl+t  (Vcs.UpdateProject)
java.action.showTypeHierarchy  <-  ctrl+h  (TypeHierarchy)
lineBreakInsert  <-  ctrl+enter  (EditorSplitLine)
merge-conflict.accept.current  <-  ctrl+alt+r  (Diff.ApplyLeftSide)
merge-conflict.accept.incoming  <-  ctrl+alt+a  (Diff.ApplyRightSide)
outline.focus  <-  alt+7  (ActivateStructureToolWindow)
redo  <-  ctrl+shift+z  ($Redo)
redo  <-  shift+alt+backspace  ($Redo)
references-view.findReferences  <-  alt+f7  (FindUsages)
references-view.showCallHierarchy  <-  ctrl+alt+h  (CallHierarchy)
scrollLineDown  <-  ctrl+down  (EditorScrollDown)
scrollLineUp  <-  ctrl+up  (EditorScrollUp)
undo  <-  alt+backspace  ($Undo)
undo  <-  ctrl+z  ($Undo)
workbench.action.closeActiveEditor  <-  ctrl+f4  (CloseContent)
workbench.action.compareEditor.previousChange  <-  shift+f7  (PreviousDiff)
workbench.action.debug.continue  <-  f9  (Resume)
workbench.action.debug.run  <-  shift+f9  (Debug)
workbench.action.debug.stepOut  <-  shift+f8  (StepOut)
workbench.action.debug.stepOver  <-  f8  (StepOver)
workbench.action.files.newUntitledFile  <-  alt+insert  (Generate)
workbench.action.files.newUntitledFile  <-  ctrl+shift+alt+insert  (NewScratchFile)
workbench.action.files.saveAll  <-  ctrl+s  (SaveAll)
workbench.action.files.showOpenedFileInNewWindow  <-  shift+f4  (EditSourceInNewWindow)
workbench.action.findInFiles  <-  ctrl+shift+f  (FindInPath)
workbench.action.gotoSymbol  <-  ctrl+f12  (FileStructurePopup)
workbench.action.gotoSymbol  <-  ctrl+shift+alt+n  (GotoSymbol)
workbench.action.maximizeEditor  <-  ctrl+shift+f12  (HideAllWindows)
workbench.action.navigateBack  <-  ctrl+alt+left  (Back)
workbench.action.navigateForward  <-  ctrl+alt+right  (Forward)
workbench.action.navigateToLastEditLocation  <-  ctrl+shift+backspace  (JumpToLastChange)
workbench.action.nextEditor  <-  alt+right  (NextTab)
workbench.action.nextEditor  <-  shift+alt+right  (NextEditorTab)
workbench.action.openGlobalSettings  <-  ctrl+alt+s  (ShowSettings)
workbench.action.openPreviousEditorFromHistory  <-  ctrl+e  (RecentFiles)
workbench.action.openRecent  <-  ctrl+e  (RecentFiles)
workbench.action.previousEditor  <-  alt+left  (PreviousTab)
workbench.action.previousEditor  <-  shift+alt+left  (PreviousEditorTab)
workbench.action.quickOpen  <-  ctrl+shift+n  (GotoFile)
workbench.action.quickOpenPreviousRecentlyUsedEditorInGroup  <-  ctrl+shift+tab  (Switcher)
workbench.action.quickOpenPreviousRecentlyUsedEditorInGroup  <-  ctrl+tab  (Switcher)
workbench.action.replaceInFiles  <-  ctrl+shift+r  (ReplaceInPath)
workbench.action.selectTheme  <-  ctrl+`  (QuickChangeScheme)
workbench.action.showAllSymbols  <-  ctrl+n  (GotoClass)
workbench.action.showCommands  <-  ctrl+shift+a  (GotoAction)
workbench.action.showErrorsWarnings  <-  ctrl+f1  (ShowErrorDescription)
workbench.action.tasks.build  <-  ctrl+f9  (CompileDirty)
workbench.action.tasks.configureTaskRunner  <-  ctrl+shift+alt+s  (ShowProjectStructureSettings)
workbench.action.tasks.reRunTask  <-  shift+f10  (Run)
workbench.action.tasks.runTask  <-  shift+alt+f10  (ChooseRunConfiguration)
workbench.action.terminal.toggleTerminal  <-  alt+f12  (ActivateTerminalToolWindow)
workbench.action.toggleSidebarVisibility  <-  shift+escape  (HideActiveWindow)
workbench.view.debug  <-  alt+5  (ActivateDebugToolWindow)
workbench.view.debug  <-  ctrl+shift+f8  (ViewBreakpoints)
workbench.view.debug  <-  shift+alt+f9  (ChooseDebugConfiguration)
workbench.view.explorer  <-  alt+1  (ActivateProjectToolWindow)
workbench.view.scm  <-  alt+9  (ActivateVersionControlToolWindow)
workbench.view.search  <-  alt+3  (ActivateFindToolWindow)
```

## Already covered by base / extension (skipped)  (24)

```
CodeFloatingToolbar.GotoNextMenu  (explicitly dropped by overrides.jsonc)
CollapseAll  (explicitly dropped by overrides.jsonc)
CollapseRegionRecursively  (explicitly dropped by overrides.jsonc)
CompareTwoFiles  (explicitly dropped by overrides.jsonc)
Diff.FocusOppositePane  (explicitly dropped by overrides.jsonc)
Diff.ShowDiff  (explicitly dropped by overrides.jsonc)
ExpandAll  (explicitly dropped by overrides.jsonc)
ExpandRegionRecursively  (explicitly dropped by overrides.jsonc)
NextDiff  (explicitly dropped by overrides.jsonc)
SearchEverywhere.NextTab  (explicitly dropped by overrides.jsonc)
SearchEverywhere.PrevTab  (explicitly dropped by overrides.jsonc)
StepInto  (explicitly dropped by overrides.jsonc)
Terminal.ClearPrompt  (explicitly dropped by overrides.jsonc)
acceptSelectedSuggestion  <-  enter  (EditorChooseLookupItem)
cursorPageDown  <-  pagedown  (EditorPageDown)
cursorPageDownSelect  <-  shift+pagedown  (EditorPageDownWithSelection)
cursorPageUp  <-  pageup  (EditorPageUp)
cursorPageUpSelect  <-  shift+pageup  (EditorPageUpWithSelection)
editor.action.marker.next  <-  f2  (GotoNextError)
editor.action.marker.prev  <-  shift+f2  (GotoPreviousError)
editor.action.nextMatchFindAction  <-  f3  (FindNext)
editor.action.previousMatchFindAction  <-  shift+f3  (FindPrevious)
editor.action.triggerSuggest  <-  ctrl+space  (CodeCompletion)
workbench.action.gotoLine  <-  ctrl+g  (GotoLine)
```

## No VS Code command mapping (fell through to extension / lost)  (329)

```
$Delete  <-  DELETE
ActivateBookmarksToolWindow  <-  alt 2
ActivateCommitToolWindow  <-  alt 0
ActivateNuGetToolWindow  <-  alt shift 7
ActivateProblemsViewToolWindow  <-  alt 6
ActivateRunToolWindow  <-  alt 4
ActivateServicesToolWindow  <-  alt 8
ActivateUnitTestsToolWindow  <-  alt shift 8
Arrangement.Rule.Edit  <-  F2
Arrangement.Rule.Match.Condition.Move.Down  <-  alt DOWN
Arrangement.Rule.Match.Condition.Move.Up  <-  alt UP
AutoIndentLines  <-  control alt I
BraceOrQuoteOut  <-  TAB
CallInlineCompletionAction  <-  shift alt BACK_SLASH
ChangeSignature  <-  control F6
ChangeTypeSignature  <-  control shift F6
ChangesView.AddUnversioned  <-  control alt A
ChangesView.GroupBy.Directory  <-  control alt P
ChangesView.GroupBy.Module  <-  control alt M
ChangesView.Move  <-  alt shift M
ChangesView.Rename  <-  F2, Shift F6
ChangesView.Revert  <-  control alt Z
ChangesView.SetDefault  <-  control SPACE
ChangesView.ShelveSilently  <-  shift control H
ChangesView.ShowCommitOptions  <-  control O
ChangesView.UnshelveSilently  <-  control alt U
ClassNameCompletion  <-  control alt SPACE
CloseActiveTab  <-  control shift F4
CloseDiffEditor  <-  ESCAPE
CloseGotItTooltip  <-  ESCAPE
CodeFloatingToolbar.GotoPrevMenu  <-  shift TAB
CodeInspection.OnEditor  <-  alt shift I
CollapseBlock  <-  control shift PERIOD
CollapseExpandableComponent  <-  shift ENTER, control SUBTRACT, control MINUS
CollapseSelection  <-  control PERIOD
CollapseTreeNode  <-  SUBTRACT
CollapsiblePanel-toggle  <-  SPACE
Compare.SameVersion  <-  control D
Compile  <-  control shift F9
Console.Execute  <-  ENTER
Console.Execute.Multiline  <-  control ENTER
Console.History.Browse  <-  control alt E
Console.Open  <-  control shift F10
ContextHelp  <-  F1
CopyElement  <-  F5
CopyReference  <-  control alt shift C
Diagram.DeselectAll  <-  control alt A
Diff.NextChange  <-  alt shift RIGHT
Diff.PrevChange  <-  alt shift LEFT
Diff.ShowSettingsPopup  <-  control shift D
DirDiffMenu.SynchronizeDiff  <-  ENTER
DirDiffMenu.SynchronizeDiff.All  <-  control ENTER
DumpLookupElementWeights  <-  control alt shift W
DuplicatesForm.SendToLeft  <-  control 1
DuplicatesForm.SendToRight  <-  control 2
EditBreakpoint  <-  control shift F8
EditorAddCaretPerSelectedLine  <-  shift alt G
EditorBackSpace  <-  BACK_SPACE, shift BACK_SPACE
EditorChooseLookupItemDot  <-  control PERIOD
EditorCodeBlockEnd  <-  control CLOSE_BRACKET
EditorCodeBlockEndWithSelection  <-  control shift CLOSE_BRACKET
EditorCodeBlockStart  <-  control OPEN_BRACKET
EditorCodeBlockStartWithSelection  <-  control shift OPEN_BRACKET
EditorContextInfo  <-  alt Q
EditorDecreaseFontSizeGlobal  <-  alt shift COMMA
EditorDown  <-  DOWN
EditorDownWithSelection  <-  shift DOWN
EditorEnter  <-  ENTER
EditorEscape  <-  ESCAPE
EditorFocusGutter  <-  alt shift 6 , F
EditorIncreaseFontSizeGlobal  <-  alt shift PERIOD
EditorIndentSelection  <-  TAB
EditorLeft  <-  LEFT
EditorLeftWithSelection  <-  shift LEFT
EditorLookupDown  <-  control DOWN
EditorLookupUp  <-  control UP
EditorMatchBrace  <-  control shift M
EditorPasteSimple  <-  control alt shift V
EditorRight  <-  RIGHT
EditorRightWithSelection  <-  shift RIGHT
EditorScrollToCenter  <-  control M
EditorShowGutterIconTooltip  <-  alt shift 6 , T
EditorTab  <-  TAB
EditorTextEndWithSelection  <-  control shift END
EditorTextStartWithSelection  <-  control shift HOME
EditorToggleInsertState  <-  INSERT
EditorUnindentSelection  <-  shift TAB
EditorUp  <-  UP
EditorUpWithSelection  <-  shift UP
ExpandAllToLevel1  <-  control shift MULTIPLY , 1, control shift MULTIPLY , NUMPAD1
ExpandAllToLevel2  <-  control shift MULTIPLY , 2, control shift MULTIPLY , NUMPAD2
ExpandAllToLevel3  <-  control shift MULTIPLY , 3, control shift MULTIPLY , NUMPAD3
ExpandAllToLevel4  <-  control shift MULTIPLY , 4, control shift MULTIPLY , NUMPAD4
ExpandAllToLevel5  <-  control shift MULTIPLY , 5, control shift MULTIPLY , NUMPAD5
ExpandExpandableComponent  <-  shift ENTER, control ADD, control EQUALS
ExpandLiveTemplateByTab  <-  TAB
ExpandToLevel1  <-  control MULTIPLY , 1, control MULTIPLY , NUMPAD1
ExpandToLevel2  <-  control MULTIPLY , 2, control MULTIPLY , NUMPAD2
ExpandToLevel3  <-  control MULTIPLY , 3, control MULTIPLY , NUMPAD3
ExpandToLevel4  <-  control MULTIPLY , 4, control MULTIPLY , NUMPAD4
ExpandToLevel5  <-  control MULTIPLY , 5, control MULTIPLY , NUMPAD5
ExpandTreeNode  <-  ADD
ExportToTextFile  <-  alt O
ExpressionTypeInfo  <-  control shift P
ExternalJavaDoc  <-  shift F1
ExternalSystem.ProjectRefreshAction  <-  control shift O
FileChooser.GoToParent  <-  BACK_SPACE
FileChooser.GoToRoot  <-  control BACK_SLASH
FileChooser.GotoDesktop  <-  control D
FileChooser.GotoHome  <-  control 1
FileChooser.GotoModule  <-  control 3
FileChooser.GotoProject  <-  control 2
FileChooser.NewFolder  <-  alt INSERT, control N
FileChooser.TogglePathBar  <-  control P
Find  <-  control F, alt F3
FindPrevWordAtCaret  <-  control shift F3
FindUsagesInFile  <-  control F7
FindWordAtCaret  <-  control F3
FocusEditor  <-  ESCAPE
FocusMainToolbar  <-  alt PAGE_UP
FocusStatusBar  <-  alt PAGE_DOWN
ForceRefresh  <-  control shift F5
ForceRunToCursor  <-  control alt F9
ForceStepInto  <-  alt shift F7
ForceStepOver  <-  alt shift F8
FullyExpandTreeNode  <-  MULTIPLY
Git.CreateNewBranch  <-  control alt N
Git.New.Branch.In.Log  <-  control alt N
Git.Rename.Local.Branch  <-  F2, Shift F6
Git.Reword.Commit  <-  F2, Shift F6
GotoBookmark0  <-  control 0
GotoBookmark1  <-  control 1
GotoBookmark2  <-  control 2
GotoBookmark3  <-  control 3
GotoBookmark4  <-  control 4
GotoBookmark5  <-  control 5
GotoBookmark6  <-  control 6
GotoBookmark7  <-  control 7
GotoBookmark8  <-  control 8
GotoBookmark9  <-  control 9
GotoCustomRegion  <-  control alt PERIOD
GotoRelated  <-  control alt HOME
GotoTest  <-  control shift T
HighlightUsagesInFile  <-  control shift F7
HippieBackwardCompletion  <-  alt shift SLASH
HippieCompletion  <-  alt SLASH
Images.EditExternally  <-  control alt F4
Images.Editor.ActualSize  <-  control DIVIDE, control SLASH
Images.Editor.ToggleGrid  <-  control QUOTE
ImplementMethods  <-  control I
Inline  <-  control alt N
InsertInlineCompletionAction  <-  TAB
InsertLiveTemplate  <-  control J
IntroduceConstant  <-  control alt C
IntroduceField  <-  control alt F
IntroduceParameter  <-  control alt P
JumpToLastWindow  <-  F12
Log.GoToNextError  <-  shift F7
Log.JumpToSource  <-  F7
MainMenuButton.ShowMenu  <-  alt BACK_SLASH
Markdown.Styling.CreateLink  <-  control shift U
MaximizeToolWindow  <-  control shift QUOTE
MethodHierarchy  <-  control shift H
MethodOverloadSwitchDown  <-  control DOWN
MethodOverloadSwitchUp  <-  control UP
Move  <-  F6
MoveElementLeft  <-  control alt shift LEFT
MoveElementRight  <-  control alt shift RIGHT
NewElement  <-  alt INSERT
NewElementSamePlace  <-  control alt INSERT
NextInlineCompletionSuggestionAction  <-  alt CLOSE_BRACKET
NextParameter  <-  TAB
NextProjectWindow  <-  control alt CLOSE_BRACKET
NextTemplateVariable  <-  TAB, ENTER
OpenInRightSplit  <-  shift ENTER
OverrideMethods  <-  control O
PasteMultiple  <-  control shift V, control shift INSERT
PopupHector  <-  ctrl alt shift H
PrevInlineCompletionSuggestionAction  <-  alt OPEN_BRACKET
PrevParameter  <-  shift TAB
PreviousProjectWindow  <-  control alt OPEN_BRACKET
PreviousTemplateVariable  <-  shift TAB
PublishGroup.UploadTo  <-  shift control alt X
QuickActionPopup  <-  control alt ENTER
QuickEvaluateExpression  <-  control alt F8
QuickPreview  <-  SPACE
RecentLocations  <-  control shift E
Refactorings.QuickListPopupAction  <-  control alt shift T
ReformatWithPrettierAction  <-  ctrl alt shift P
Refresh  <-  control F5
Rerun  <-  control F5
RerunTests  <-  shift alt R
ResetIdeScaleAction  <-  shift alt 0
ResizeToolWindowDown  <-  control alt shift DOWN
ResizeToolWindowLeft  <-  control alt shift LEFT
ResizeToolWindowRight  <-  control alt shift RIGHT
ResizeToolWindowUp  <-  control alt shift UP
RestoreDefaultLayout  <-  shift F12
RunClass  <-  control shift F10
RunInspection  <-  control shift alt I
SafeDelete  <-  alt DELETE
SaveAs  <-  control shift S
SearchEverywhere.CompleteCommand  <-  TAB
SearchEverywhere.NavigateToNextGroup  <-  PAGE_DOWN, control DOWN
SearchEverywhere.NavigateToPrevGroup  <-  PAGE_UP, control UP
SearchEverywhere.SelectItem  <-  Enter
SelectIn  <-  alt F1
SelectVirtualTemplateElement  <-  Alt Shift O
SendEOF  <-  control D
ServiceView.GroupByContributor  <-  control alt T
ServiceView.ShowServices  <-  control shift T
ShelveChanges.UnshelveWithDialog  <-  control shift U
ShelvedChanges.Rename  <-  F2, Shift F6
ShowBookmarks  <-  shift F11
ShowContent  <-  alt DOWN
ShowExecutionPoint  <-  alt F10
ShowFilePath  <-  control alt F12
ShowFilterPopup  <-  control alt F
ShowPopupMenu  <-  CONTEXT_MENU
ShowReformatFileDialog  <-  control shift alt L
ShowSearchHistory  <-  alt down
ShowSettingsAndFindUsages  <-  control shift alt F7
ShowTypeBookmarks  <-  control shift F11
ShowUmlDiagram  <-  control shift alt U
ShowUmlDiagramPopup  <-  control alt U
SmartStepInto  <-  shift F7
SmartTypeCompletion  <-  control shift SPACE
SplitChooser  <-  alt shift ENTER
SplitChooser.Duplicate  <-  ctrl ENTER
SplitChooser.NextWindow  <-  TAB
SplitChooser.PreviousWindow  <-  shift TAB
SplitChooser.Split  <-  ENTER
SplitChooser.SplitCenter  <-  SPACE
Stop  <-  control F2
StopBackgroundProcesses  <-  control shift F2
SurroundWith  <-  control alt T
SurroundWithLiveTemplate  <-  control alt J
SwitchCoverage  <-  control alt F6
SwitchHeaderSource  <-  F10
SwitcherIterateItems  <-  control E
SwitcherRecentEditedChangedToggleCheckBox  <-  control E
Synchronize  <-  control alt Y
Table-selectFirstRow  <-  control UP
Table-selectFirstRowExtendSelection  <-  control shift UP
Table-selectLastRow  <-  control DOWN
Table-selectLastRowExtendSelection  <-  control shift DOWN
Table-startEditing  <-  F2
Terminal.CloseSession  <-  control D
Terminal.CopySelectedText  <-  control C, control INSERT
Terminal.DeletePreviousWord  <-  control W
Terminal.LineDown  <-  control DOWN
Terminal.LineUp  <-  control UP
Terminal.PageDown  <-  shift PAGE_DOWN
Terminal.PageUp  <-  shift PAGE_UP
Terminal.SearchInCommandHistory  <-  control R
Terminal.SelectBlockAbove  <-  UP, control UP
Terminal.SelectBlockBelow  <-  DOWN
Terminal.SelectLastBlock  <-  control UP
Terminal.SelectPrompt  <-  control DOWN
Terminal.SmartCommandExecution.Debug  <-  control shift ENTER
Terminal.SmartCommandExecution.Run  <-  control ENTER
TextSearchAction  <-  control shift alt E
TodoViewGroupByFlattenPackage  <-  control alt C
TodoViewGroupByShowModules  <-  control alt M
TodoViewGroupByShowPackages  <-  control alt P
ToggleBookmark  <-  F11
ToggleBookmark0  <-  control shift 0
ToggleBookmark1  <-  control shift 1
ToggleBookmark2  <-  control shift 2
ToggleBookmark3  <-  control shift 3
ToggleBookmark4  <-  control shift 4
ToggleBookmark5  <-  control shift 5
ToggleBookmark6  <-  control shift 6
ToggleBookmark7  <-  control shift 7
ToggleBookmark8  <-  control shift 8
ToggleBookmark9  <-  control shift 9
ToggleBookmarkWithMnemonic  <-  control F11
ToggleFindInSelection  <-  control alt E
ToggleRenderedDocPresentation  <-  control alt Q
ToggleTemporaryLineBreakpoint  <-  control shift alt F8
Tree-startEditing  <-  F2
Uml.CollapseNodes  <-  C
Uml.ExpandNodes  <-  E
Unwrap  <-  control shift DELETE
UpdateRunningApplication  <-  control F10
UsageFiltering.Imports  <-  control I
UsageFiltering.ReadAccess  <-  control R
UsageFiltering.WriteAccess  <-  control W
UsageGrouping.Directory  <-  control alt P
UsageGrouping.DirectoryStructure  <-  control alt D
UsageGrouping.FileStructure  <-  control alt F
UsageGrouping.FlattenModules  <-  control alt O
UsageGrouping.Module  <-  control alt M
UsageGrouping.UsageType  <-  control alt T
UsageView.Include  <-  INSERT
Vcs.CombinedDiff.CaretToNextBlock  <-  RIGHT, PAGE_DOWN
Vcs.CombinedDiff.CaretToPrevBlock  <-  LEFT, PAGE_UP
Vcs.CombinedDiff.ToggleCollapseBlock  <-  control ESCAPE
Vcs.MoveChangedLinesToChangelist  <-  alt shift M
Vcs.QuickListPopupAction  <-  alt BACK_QUOTE
Vcs.ShowMessageHistory  <-  control M
Vcs.ToggleAmendCommitMode  <-  alt M
VcsHistory.ShowAllAffected  <-  alt shift A
ViewSource  <-  control ENTER
WD.UploadCurrentRemoteFileAction  <-  shift alt Q
WebOpenInAction  <-  alt F2
XDebugger.AttachToProcess  <-  control alt F5
XDebugger.JumpToTypeSource  <-  shift F4
XDebugger.NewWatch  <-  INSERT
XDebugger.SetValue  <-  F2
XPathView.Actions.Evaluate  <-  control alt X , E
XPathView.Actions.FindByExpression  <-  control alt X , F
XPathView.Actions.ShowPath  <-  control alt X , P
ZoomInIdeAction  <-  shift alt EQUALS
ZoomOutIdeAction  <-  shift alt MINUS
com.jetbrains.php.framework.FrameworkRunConsoleAction  <-  control shift X
com.laravel_idea.plugin.GenerateHelperCodeAction  <-  control shift PERIOD
com.laravel_idea.plugin.LaravelActionChooser  <-  control shift COMMA
context.clear  <-  alt shift X
context.load  <-  alt shift L
context.save  <-  alt shift S
org.intellij.plugins.markdown.ui.actions.styling.ToggleBoldAction  <-  control B
org.intellij.plugins.markdown.ui.actions.styling.ToggleCodeSpanAction  <-  control shift C
org.intellij.plugins.markdown.ui.actions.styling.ToggleItalicAction  <-  control I
org.intellij.plugins.markdown.ui.actions.styling.ToggleStrikethroughAction  <-  control shift S
tasks.close  <-  alt shift W
tasks.goto  <-  alt shift N
tasks.open.in.browser  <-  alt shift B
tasks.switch  <-  alt shift T
```

## Key could not be translated  (0)

_none_

## Mouse shortcuts (not portable to keybindings.json)  (14)

```
Back  <-  mouse: button4
EditorAddOrRemoveCaret  <-  mouse: alt button1
EditorAddRectangularSelectionOnMouseDrag  <-  mouse: ctrl alt shift button1
EditorCreateRectangularSelection  <-  mouse: alt shift button2
EditorCreateRectangularSelectionOnMouseDrag  <-  mouse: alt shift button1
EditorCreateRectangularSelectionOnMouseDrag  <-  mouse: button2
EditorPasteFromX11  <-  mouse: button2
Forward  <-  mouse: button5
GotoDeclaration  <-  mouse: ctrl button1
GotoImplementation  <-  mouse: ctrl alt button1
GotoTypeDeclaration  <-  mouse: ctrl shift button1
OpenInRightSplit  <-  mouse: alt button1 doubleClick
QuickEvaluateExpression  <-  mouse: alt shift button1
QuickJavaDoc  <-  mouse: alt button2
```
