# PhpStorm -> VS Code keymap port report

- source actions parsed: **591**
- generated entries: **119**
- curated base entries (overrides.jsonc): **56**
- total in keybindings.generated.json: **175**

## Mapped -> emitted  (119)

```
acceptAlternativeSelectedSuggestion  <-  tab  (EditorChooseLookupItemReplace)
acceptSelectedSuggestion  <-  ctrl+shift+enter  (EditorCompleteStatement)
breadcrumbs.focus  <-  alt+home  (ShowNavBar)
copyFilePath  <-  ctrl+shift+c  (CopyPaths)
cursorBottom  <-  ctrl+pagedown  (EditorMoveToPageBottom)
cursorBottomSelect  <-  ctrl+shift+pagedown  (EditorMoveToPageBottomWithSelection)
cursorLineEnd  <-  end  (EditorLineEnd)
cursorLineEndSelect  <-  shift+end  (EditorLineEndWithSelection)
cursorLineStart  <-  home  (EditorLineStart)
cursorLineStartSelect  <-  shift+home  (EditorLineStartWithSelection)
cursorTop  <-  ctrl+pageup  (EditorMoveToPageTop)
cursorTopSelect  <-  ctrl+shift+pageup  (EditorMoveToPageTopWithSelection)
cursorUndo  <-  shift+alt+j  (UnselectPreviousOccurrence)
editor.action.addSelectionToNextFindMatch  <-  alt+j  (SelectNextOccurrence)
editor.action.blockComment  <-  ctrl+shift+/  (CommentByBlockComment)
editor.action.blockComment  <-  ctrl+shift+numpad_divide  (CommentByBlockComment)
editor.action.codeAction  <-  ctrl+alt+m  (ExtractMethod)
editor.action.codeAction  <-  ctrl+alt+v  (IntroduceVariable)
editor.action.dirtydiff.next  <-  ctrl+shift+alt+down  (VcsShowNextChangeMarker)
editor.action.dirtydiff.previous  <-  ctrl+shift+alt+up  (VcsShowPrevChangeMarker)
editor.action.formatDocument  <-  ctrl+alt+l  (ReformatCode)
editor.action.goToImplementation  <-  ctrl+alt+b  (GotoImplementation)
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
editor.action.selectHighlights  <-  ctrl+shift+alt+j  (SelectAllOccurrences)
editor.action.showHover  <-  ctrl+q  (QuickJavaDoc)
editor.action.toggleColumnSelection  <-  shift+alt+insert  (EditorToggleColumnMode)
editor.action.transformToUppercase  <-  ctrl+shift+u  (EditorToggleCase)
editor.action.triggerParameterHints  <-  ctrl+p  (ParameterInfo)
editor.debug.action.runToCursor  <-  alt+f9  (RunToCursor)
editor.debug.action.selectionToRepl  <-  alt+f8  (EvaluateExpression)
editor.debug.action.toggleBreakpoint  <-  ctrl+f8  (ToggleLineBreakpoint)
editor.fold  <-  ctrl+-  (CollapseRegion)
editor.fold  <-  ctrl+numpad_subtract  (CollapseRegion)
editor.foldAll  <-  ctrl+-  (CollapseAll)
editor.foldAll  <-  ctrl+numpad_subtract  (CollapseAll)
editor.foldAll  <-  ctrl+shift+-  (CollapseAllRegions)
editor.foldAll  <-  ctrl+shift+numpad_subtract  (CollapseAllRegions)
editor.unfold  <-  ctrl+=  (ExpandRegion)
editor.unfold  <-  ctrl+numpad_add  (ExpandRegion)
editor.unfoldAll  <-  ctrl+=  (ExpandAll)
editor.unfoldAll  <-  ctrl+numpad_add  (ExpandAll)
editor.unfoldAll  <-  ctrl+shift+=  (ExpandAllRegions)
editor.unfoldAll  <-  ctrl+shift+numpad_add  (ExpandAllRegions)
git.pushTo  <-  ctrl+alt+k  (Git.Commit.And.Push.Executor)
git.revertSelectedRanges  <-  ctrl+alt+z  (Vcs.RollbackChangedLines)
git.sync  <-  ctrl+t  (Vcs.UpdateProject)
java.action.showTypeHierarchy  <-  ctrl+h  (TypeHierarchy)
lineBreakInsert  <-  ctrl+enter  (EditorSplitLine)
merge-conflict.accept.current  <-  ctrl+alt+r  (Diff.ApplyLeftSide)
merge-conflict.accept.incoming  <-  ctrl+alt+a  (Diff.ApplyRightSide)
outline.focus  <-  alt+7  (ActivateStructureToolWindow)
redo  <-  shift+alt+backspace  ($Redo)
references-view.findReferences  <-  alt+f7  (FindUsages)
references-view.showCallHierarchy  <-  ctrl+alt+h  (CallHierarchy)
scrollLineDown  <-  ctrl+down  (EditorScrollDown)
scrollLineUp  <-  ctrl+up  (EditorScrollUp)
undo  <-  alt+backspace  ($Undo)
workbench.action.compareEditor.nextChange  <-  f7  (NextDiff)
workbench.action.compareEditor.previousChange  <-  shift+f7  (PreviousDiff)
workbench.action.debug.continue  <-  f9  (Resume)
workbench.action.debug.run  <-  shift+f9  (Debug)
workbench.action.debug.stepInto  <-  f7  (StepInto)
workbench.action.debug.stepOut  <-  shift+f8  (StepOut)
workbench.action.debug.stepOver  <-  f8  (StepOver)
workbench.action.files.newUntitledFile  <-  alt+insert  (Generate)
workbench.action.files.newUntitledFile  <-  ctrl+shift+alt+insert  (NewScratchFile)
workbench.action.files.saveAll  <-  ctrl+s  (SaveAll)
workbench.action.files.showOpenedFileInNewWindow  <-  shift+f4  (EditSourceInNewWindow)
workbench.action.gotoSymbol  <-  ctrl+f12  (FileStructurePopup)
workbench.action.gotoSymbol  <-  ctrl+shift+alt+n  (GotoSymbol)
workbench.action.maximizeEditor  <-  ctrl+shift+f12  (HideAllWindows)
workbench.action.navigateBack  <-  ctrl+alt+left  (Back)
workbench.action.navigateForward  <-  ctrl+alt+right  (Forward)
workbench.action.navigateToLastEditLocation  <-  ctrl+shift+backspace  (JumpToLastChange)
workbench.action.nextEditor  <-  alt+right  (NextTab)
workbench.action.nextEditor  <-  shift+alt+right  (NextEditorTab)
workbench.action.openGlobalSettings  <-  ctrl+alt+s  (ShowSettings)
workbench.action.previousEditor  <-  alt+left  (PreviousTab)
workbench.action.previousEditor  <-  shift+alt+left  (PreviousEditorTab)
workbench.action.quickOpen  <-  ctrl+shift+n  (GotoFile)
workbench.action.quickOpenNavigateNext  <-  ctrl+shift+tab  (Diff.FocusOppositePane)
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

## Already covered by base / extension (skipped)  (51)

```
CodeFloatingToolbar.GotoNextMenu  (explicitly dropped in overrides.jsonc)
CollapseRegionRecursively  (explicitly dropped in overrides.jsonc)
CompareTwoFiles  (explicitly dropped in overrides.jsonc)
Diff.ShowDiff  (explicitly dropped in overrides.jsonc)
ExpandRegionRecursively  (explicitly dropped in overrides.jsonc)
SearchEverywhere.NextTab  (explicitly dropped in overrides.jsonc)
SearchEverywhere.PrevTab  (explicitly dropped in overrides.jsonc)
Terminal.ClearPrompt  (explicitly dropped in overrides.jsonc)
acceptSelectedSuggestion  <-  enter  (EditorChooseLookupItem)
com.anthropic.code.plugin.actions.OpenClaudeInTerminalAction  (explicitly dropped in overrides.jsonc)
cursorBottom  <-  ctrl+end  (EditorTextEnd)
cursorPageDown  <-  pagedown  (EditorPageDown)
cursorPageDownSelect  <-  shift+pagedown  (EditorPageDownWithSelection)
cursorPageUp  <-  pageup  (EditorPageUp)
cursorPageUpSelect  <-  shift+pageup  (EditorPageUpWithSelection)
cursorTop  <-  ctrl+home  (EditorTextStart)
cursorWordLeft  <-  ctrl+left  (EditorPreviousWord)
cursorWordLeftSelect  <-  ctrl+shift+left  (EditorPreviousWordWithSelection)
cursorWordRight  <-  ctrl+right  (EditorNextWord)
cursorWordRightSelect  <-  ctrl+shift+right  (EditorNextWordWithSelection)
deleteWordLeft  <-  ctrl+backspace  (EditorDeleteToWordStart)
deleteWordRight  <-  ctrl+delete  (EditorDeleteToWordEnd)
editor.action.clipboardCopyAction  <-  ctrl+c  ($Copy)
editor.action.clipboardCopyAction  <-  ctrl+insert  ($Copy)
editor.action.clipboardCutAction  <-  ctrl+x  ($Cut)
editor.action.clipboardCutAction  <-  shift+delete  ($Cut)
editor.action.clipboardPasteAction  <-  ctrl+v  ($Paste)
editor.action.clipboardPasteAction  <-  shift+insert  ($Paste)
editor.action.commentLine  <-  ctrl+/  (CommentByLineComment)
editor.action.commentLine  <-  ctrl+numpad_divide  (CommentByLineComment)
editor.action.copyLinesDownAction  <-  ctrl+d  (EditorDuplicate)
editor.action.deleteLines  <-  ctrl+y  (EditorDeleteLine)
editor.action.goToImplementation  <-  ctrl+u  (GotoSuperMethod)
editor.action.marker.next  <-  f2  (GotoNextError)
editor.action.marker.prev  <-  shift+f2  (GotoPreviousError)
editor.action.nextMatchFindAction  <-  ctrl+l  (FindNext)
editor.action.nextMatchFindAction  <-  f3  (FindNext)
editor.action.previousMatchFindAction  <-  shift+f3  (FindPrevious)
editor.action.selectAll  <-  ctrl+a  ($SelectAll)
editor.action.smartSelect.grow  <-  ctrl+w  (EditorSelectWord)
editor.action.smartSelect.shrink  <-  ctrl+shift+w  (EditorUnSelectWord)
editor.action.startFindReplaceAction  <-  ctrl+r  (Replace)
editor.action.triggerSuggest  <-  ctrl+space  (CodeCompletion)
git.commitAll  <-  ctrl+k  (CheckinProject)
redo  <-  ctrl+shift+z  ($Redo)
undo  <-  ctrl+z  ($Undo)
workbench.action.closeActiveEditor  <-  ctrl+f4  (CloseContent)
workbench.action.findInFiles  <-  ctrl+shift+f  (FindInPath)
workbench.action.gotoLine  <-  ctrl+g  (GotoLine)
workbench.action.openPreviousEditorFromHistory  <-  ctrl+e  (RecentFiles)
workbench.action.openRecent  <-  ctrl+e  (RecentFiles)
```

## No VS Code command mapping (fell through to extension / lost)  (431)

```
$Delete  <-  DELETE
AIAssistant.Editor.AskAiAssistantInEditor  <-  ctrl BACK_SLASH
ActivateBookmarksToolWindow  <-  alt 2
ActivateCommitToolWindow  <-  alt 0
ActivateNuGetToolWindow  <-  shift alt 7
ActivateProblemsViewToolWindow  <-  alt 6
ActivateRunToolWindow  <-  alt 4
ActivateServicesToolWindow  <-  alt 8
ActivateUnitTestsToolWindow  <-  shift alt 8
Arrangement.Rule.Edit  <-  F2
Arrangement.Rule.Match.Condition.Move.Down  <-  alt DOWN
Arrangement.Rule.Match.Condition.Move.Up  <-  alt UP
AutoIndentLines  <-  ctrl alt I
BraceOrQuoteOut  <-  TAB
CWMHostShowPopupAction  <-  shift ctrl Y
CallInlineCompletionAction  <-  shift alt BACK_SLASH
ChangeSignature  <-  ctrl F6
ChangeTypeSignature  <-  shift ctrl F6
ChangesView.AddUnversioned  <-  ctrl alt A
ChangesView.GroupBy.Directory  <-  ctrl alt P
ChangesView.GroupBy.Module  <-  ctrl alt M
ChangesView.Move  <-  shift alt M
ChangesView.Rename  <-  F2, shift F6
ChangesView.Revert  <-  ctrl alt Z
ChangesView.SetDefault  <-  ctrl SPACE
ChangesView.ShelveSilently  <-  shift ctrl H
ChangesView.ShowCommitOptions  <-  ctrl O
ChangesView.UnshelveSilently  <-  ctrl alt U
ClassNameCompletion  <-  ctrl alt SPACE
CloseActiveTab  <-  shift ctrl F4
CloseDiffEditor  <-  ESCAPE
CloseGotItTooltip  <-  ESCAPE
Code.Review.Editor.New.Comment  <-  shift ctrl X
CodeFloatingToolbar.GotoPrevMenu  <-  shift TAB
CodeInspection.OnEditor  <-  shift alt I
CollapseBlock  <-  shift ctrl PERIOD
CollapseExpandableComponent  <-  shift ENTER, ctrl SUBTRACT, ctrl MINUS
CollapseSelection  <-  ctrl PERIOD
CollapseTreeNode  <-  SUBTRACT
CollapsiblePanel-toggle  <-  SPACE
Compare.SameVersion  <-  ctrl D
Compile  <-  shift ctrl F9
Console.Execute  <-  ENTER
Console.Execute.Multiline  <-  ctrl ENTER
Console.History.Browse  <-  ctrl alt E
Console.Open  <-  shift ctrl F10
Console.TableResult.CloneColumn  <-  shift ctrl alt D
Console.TableResult.ColumnSortReset  <-  shift ctrl alt BACK_SPACE
Console.TableResult.ColumnVisibility  <-  SPACE
Console.TableResult.CompareCells  <-  shift ctrl D
Console.TableResult.DeleteColumns  <-  shift alt DELETE
Console.TableResult.EditFilterCriteria  <-  shift ctrl alt F
Console.TableResult.EditValue  <-  ENTER, alt ENTER, F2
Console.TableResult.EditValueMaximized  <-  shift ENTER, shift alt ENTER
Console.TableResult.GotoReferencedResult  <-  ENTER, alt ENTER, F2
Console.TableResult.MaximizeEditingCell  <-  shift ctrl alt M
Console.TableResult.NextPage  <-  ctrl alt DOWN
Console.TableResult.PreviousPage  <-  ctrl alt UP
Console.TableResult.SelectRow  <-  shift SPACE
Console.TableResult.SetDefault  <-  ctrl alt D
Console.TableResult.SetNull  <-  ctrl alt N
Console.TableResult.ShowRecordView  <-  shift ctrl ENTER
Console.TableResult.SubmitAndCommit  <-  shift ctrl alt ENTER
Console.Transaction.Commit  <-  shift ctrl alt ENTER
ContextHelp  <-  F1
CopyElement  <-  F5
CopyReference  <-  shift ctrl alt C
CurrentLeadUnfollowAction  <-  shift ctrl alt Y
DatabaseView.CopyDdlAction  <-  shift ctrl alt G, shift ctrl C
DatabaseView.DropAction  <-  DELETE
DatabaseView.FullTextSearch  <-  shift ctrl alt F
DatabaseView.OpenDdlInConsole  <-  shift ctrl alt B
DatabaseView.PropertiesAction  <-  shift ENTER
DatabaseView.SqlGenerator  <-  ctrl alt G
Diagram.DeselectAll  <-  ctrl alt A
Diff.NextChange  <-  shift alt RIGHT
Diff.PrevChange  <-  shift alt LEFT
Diff.ShowSettingsPopup  <-  shift ctrl D
DirDiffMenu.SynchronizeDiff  <-  ENTER
DirDiffMenu.SynchronizeDiff.All  <-  ctrl ENTER
Docker.RemoteServers.StartComposeService  <-  ctrl ENTER
DomCollectionControl.Add  <-  INSERT
DownloadBackendFileToClient  <-  shift ctrl D
DumpLookupElementWeights  <-  shift ctrl alt W
DumpMLCompletionFeatures  <-  shift ctrl alt 9
DuplicatesForm.SendToLeft  <-  ctrl 1
DuplicatesForm.SendToRight  <-  ctrl 2
EditBreakpoint  <-  shift ctrl F8
EditorAddCaretPerSelectedLine  <-  shift alt G
EditorBackSpace  <-  BACK_SPACE, shift BACK_SPACE
EditorChooseLookupItemDot  <-  ctrl PERIOD
EditorCodeBlockEnd  <-  ctrl CLOSE_BRACKET
EditorCodeBlockEndWithSelection  <-  shift ctrl CLOSE_BRACKET
EditorCodeBlockStart  <-  ctrl OPEN_BRACKET
EditorCodeBlockStartWithSelection  <-  shift ctrl OPEN_BRACKET
EditorContextInfo  <-  alt Q
EditorDecreaseFontSizeGlobal  <-  shift alt COMMA
EditorDown  <-  DOWN
EditorDownWithSelection  <-  shift DOWN
EditorEnter  <-  ENTER
EditorEscape  <-  ESCAPE
EditorFocusGutter  <-  shift alt 6 , F
EditorIncreaseFontSizeGlobal  <-  shift alt PERIOD
EditorIndentSelection  <-  TAB
EditorLeft  <-  LEFT
EditorLeftWithSelection  <-  shift LEFT
EditorLookupDown  <-  ctrl DOWN
EditorLookupUp  <-  ctrl UP
EditorMatchBrace  <-  shift ctrl M
EditorPasteSimple  <-  shift ctrl alt V
EditorRight  <-  RIGHT
EditorRightWithSelection  <-  shift RIGHT
EditorScrollToCenter  <-  ctrl M
EditorShowGutterIconTooltip  <-  shift alt 6 , T
EditorTab  <-  TAB
EditorTextEndWithSelection  <-  shift ctrl END
EditorTextStartWithSelection  <-  shift ctrl HOME
EditorToggleInsertState  <-  INSERT
EditorUnindentSelection  <-  shift TAB
EditorUp  <-  UP
EditorUpWithSelection  <-  shift UP
EmmetNextEditPoint  <-  shift alt CLOSE_BRACKET
EmmetPreviousEditPoint  <-  shift alt OPEN_BRACKET
EmojiPicker.Open  <-  ctrl alt SEMICOLON
EscUnfollowUserAction  <-  ESCAPE
ExpandAllToLevel1  <-  shift ctrl MULTIPLY , 1, shift ctrl MULTIPLY , NUMPAD1
ExpandAllToLevel2  <-  shift ctrl MULTIPLY , 2, shift ctrl MULTIPLY , NUMPAD2
ExpandAllToLevel3  <-  shift ctrl MULTIPLY , 3, shift ctrl MULTIPLY , NUMPAD3
ExpandAllToLevel4  <-  shift ctrl MULTIPLY , 4, shift ctrl MULTIPLY , NUMPAD4
ExpandAllToLevel5  <-  shift ctrl MULTIPLY , 5, shift ctrl MULTIPLY , NUMPAD5
ExpandExpandableComponent  <-  shift ENTER, ctrl ADD, ctrl EQUALS
ExpandLiveTemplateByTab  <-  TAB
ExpandToLevel1  <-  ctrl MULTIPLY , 1, ctrl MULTIPLY , NUMPAD1
ExpandToLevel2  <-  ctrl MULTIPLY , 2, ctrl MULTIPLY , NUMPAD2
ExpandToLevel3  <-  ctrl MULTIPLY , 3, ctrl MULTIPLY , NUMPAD3
ExpandToLevel4  <-  ctrl MULTIPLY , 4, ctrl MULTIPLY , NUMPAD4
ExpandToLevel5  <-  ctrl MULTIPLY , 5, ctrl MULTIPLY , NUMPAD5
ExpandTreeNode  <-  ADD
ExportToTextFile  <-  alt O
ExpressionTypeInfo  <-  shift ctrl P
ExternalJavaDoc  <-  shift F1
ExternalSystem.ProjectRefreshAction  <-  shift ctrl O
FileChooser.GoToParent  <-  BACK_SPACE
FileChooser.GoToRoot  <-  ctrl BACK_SLASH
FileChooser.GotoDesktop  <-  ctrl D
FileChooser.GotoHome  <-  ctrl 1
FileChooser.GotoModule  <-  ctrl 3
FileChooser.GotoProject  <-  ctrl 2
FileChooser.NewFolder  <-  alt INSERT, ctrl N
FileChooser.TogglePathBar  <-  ctrl P
Find  <-  ctrl F, alt F3
FindPrevWordAtCaret  <-  shift ctrl F3
FindUsagesInFile  <-  ctrl F7
FindWordAtCaret  <-  ctrl F3
FocusEditor  <-  ESCAPE
ForceOthersToFollowAction  <-  shift ctrl O
ForceRefresh  <-  shift ctrl F5
ForceRunToCursor  <-  ctrl alt F9
ForceStepInto  <-  shift alt F7
ForceStepOver  <-  shift alt F8
Frontend.ChangesView.UnshelveSilently  <-  ctrl alt U
FullyExpandTreeNode  <-  MULTIPLY
Git.Branches  <-  shift ctrl BACK_QUOTE
Git.CreateNewBranch  <-  ctrl alt N
Git.Log.Branches.Change.Branch.Filter  <-  ENTER
Git.New.Branch.In.Log  <-  ctrl alt N
Git.Rename.Local.Branch  <-  F2, shift F6
Git.Reword.Commit  <-  F2, shift F6
Github.PullRequest.Changed.MarkViewed.Toggle  <-  shift ctrl S
GotoBookmark0  <-  ctrl 0
GotoBookmark1  <-  ctrl 1
GotoBookmark2  <-  ctrl 2
GotoBookmark3  <-  ctrl 3
GotoBookmark4  <-  ctrl 4
GotoBookmark5  <-  ctrl 5
GotoBookmark6  <-  ctrl 6
GotoBookmark7  <-  ctrl 7
GotoBookmark8  <-  ctrl 8
GotoBookmark9  <-  ctrl 9
GotoCustomRegion  <-  ctrl alt PERIOD
GotoRelated  <-  ctrl alt HOME
GotoTest  <-  shift ctrl T
Graph.ActualSize  <-  ctrl DIVIDE, ctrl SLASH
Graph.AlignNodes.Bottom  <-  shift B
Graph.AlignNodes.Center  <-  shift C
Graph.AlignNodes.Left  <-  shift L
Graph.AlignNodes.Middle  <-  shift M
Graph.AlignNodes.Right  <-  shift R
Graph.AlignNodes.Top  <-  shift T
Graph.ApplyCurrentLayout  <-  shift F5
Graph.DistributeNodes.Horizontally  <-  shift H
Graph.DistributeNodes.Vertically  <-  shift V
Graph.RouteEdges  <-  F5
Graph.ZoomIn  <-  ADD, EQUALS
Graph.ZoomOut  <-  SUBTRACT, MINUS
Hg.Commit.And.Push.Executor  <-  ctrl alt K
HighlightUsagesInFile  <-  shift ctrl F7
HippieBackwardCompletion  <-  shift alt SLASH
HippieCompletion  <-  alt SLASH
Images.EditExternally  <-  ctrl alt F4
Images.Editor.ActualSize  <-  ctrl DIVIDE, ctrl SLASH
Images.Editor.ToggleGrid  <-  ctrl QUOTE
ImplementMethods  <-  ctrl I
Inline  <-  ctrl alt N
InlinePromptGenerateCodeAction  <-  TAB
InsertInlineCompletionAction  <-  TAB
InsertLiveTemplate  <-  ctrl J
IntroduceConstant  <-  ctrl alt C
IntroduceField  <-  ctrl alt F
IntroduceParameter  <-  ctrl alt P
JavaScript.ShowComponentUsages  <-  shift ctrl D
Jdbc.OpenConsole.New  <-  shift ctrl Q
Jdbc.OpenConsole.Scratch  <-  shift ctrl alt Q
JumpToLastWindow  <-  F12
Log.GoToNextError  <-  shift F7
Log.JumpToSource  <-  F7
MTNextFavoriteThemeAction  <-  shift ctrl meta alt N
MTPreviousFavoriteThemeAction  <-  shift ctrl meta alt P
MainMenuButton.ShowMenu  <-  alt BACK_SLASH
Markdown.Styling.CreateLink  <-  shift ctrl U
MaximizeToolWindow  <-  shift ctrl QUOTE
MethodHierarchy  <-  shift ctrl H
MethodOverloadSwitchDown  <-  ctrl DOWN
MethodOverloadSwitchUp  <-  ctrl UP
Move  <-  F6
MoveElementLeft  <-  shift ctrl alt LEFT
MoveElementRight  <-  shift ctrl alt RIGHT
NewElement  <-  alt INSERT
NewElementSamePlace  <-  ctrl alt INSERT
NextInlineCompletionSuggestionAction  <-  alt CLOSE_BRACKET
NextParameter  <-  TAB
NextProjectWindow  <-  ctrl alt CLOSE_BRACKET
NextTemplateVariable  <-  TAB, ENTER
OpenInRightSplit  <-  shift ENTER
OverrideMethods  <-  ctrl O
PasteMultiple  <-  shift ctrl V, shift ctrl INSERT
PerforceDirect.Edit  <-  ctrl alt E
PopupHector  <-  shift ctrl alt H
PrevInlineCompletionSuggestionAction  <-  alt OPEN_BRACKET
PrevParameter  <-  shift TAB
PreviousProjectWindow  <-  ctrl alt OPEN_BRACKET
PreviousTemplateVariable  <-  shift TAB
PublishGroup.UploadTo  <-  shift ctrl alt X
QuickActionPopup  <-  ctrl alt ENTER
QuickEvaluateExpression  <-  ctrl alt F8
QuickPreview  <-  SPACE
RecentChanges  <-  shift alt C
RecentLocations  <-  shift ctrl E
Refactorings.QuickListPopupAction  <-  shift ctrl alt T
ReformatWithPrettierAction  <-  shift ctrl alt P
Refresh  <-  ctrl F5
Rerun  <-  ctrl F5
RerunTests  <-  shift alt R
ResetIdeScaleAction  <-  shift alt 0
ResizeToolWindowDown  <-  shift ctrl alt DOWN
ResizeToolWindowLeft  <-  shift ctrl alt LEFT
ResizeToolWindowRight  <-  shift ctrl alt RIGHT
ResizeToolWindowUp  <-  shift ctrl alt UP
RestoreDefaultLayout  <-  shift F12
RunClass  <-  shift ctrl F10
RunInspection  <-  shift ctrl alt I
RunJsbtTask  <-  alt F11
SafeDelete  <-  alt DELETE
SaveAs  <-  shift ctrl S
SearchEverywhere.CompleteCommand  <-  TAB
SearchEverywhere.NavigateToNextGroup  <-  PAGE_DOWN, ctrl DOWN
SearchEverywhere.NavigateToPrevGroup  <-  PAGE_UP, ctrl UP
SearchEverywhere.SelectItem  <-  ENTER
SelectIn  <-  alt F1
SelectVirtualTemplateElement  <-  shift alt O
SendEOF  <-  ctrl D
ServiceView.GroupByContributor  <-  ctrl alt T
ServiceView.ShowServices  <-  shift ctrl T
ShelveChanges.UnshelveWithDialog  <-  shift ctrl U
ShelvedChanges.Rename  <-  F2, shift F6
ShowBookmarks  <-  shift F11
ShowContent  <-  alt DOWN
ShowExecutionPoint  <-  alt F10
ShowFilePath  <-  ctrl alt F12
ShowFilterPopup  <-  ctrl alt F
ShowPopupMenu  <-  CONTEXT_MENU
ShowReformatFileDialog  <-  shift ctrl alt L
ShowSearchHistory  <-  alt DOWN
ShowSettingsAndFindUsages  <-  shift ctrl alt F7
ShowTypeBookmarks  <-  shift ctrl F11
ShowUmlDiagram  <-  shift ctrl alt U
ShowUmlDiagramPopup  <-  ctrl alt U
SingleUserFollowAction  <-  shift ctrl alt Y
SmartStepInto  <-  shift F7
SmartTypeCompletion  <-  shift ctrl SPACE
SplitChooser  <-  shift alt ENTER
SplitChooser.Duplicate  <-  ctrl ENTER
SplitChooser.NextWindow  <-  TAB
SplitChooser.PreviousWindow  <-  shift TAB
SplitChooser.Split  <-  ENTER
SplitChooser.SplitCenter  <-  SPACE
Stop  <-  ctrl F2
StopBackgroundProcesses  <-  shift ctrl F2
SurroundWith  <-  ctrl alt T
SurroundWithLiveTemplate  <-  ctrl alt J
SwitchCoverage  <-  ctrl alt F6
SwitchHeaderSource  <-  F10
SwitcherIterateItems  <-  ctrl E
SwitcherRecentEditedChangedToggleCheckBox  <-  ctrl E
Synchronize  <-  ctrl alt Y
Table-startEditing  <-  F2
Terminal.CloseSession  <-  ctrl D
Terminal.CommandCompletion  <-  TAB
Terminal.CopySelectedText  <-  ctrl C, ctrl INSERT
Terminal.DeletePreviousWord  <-  ctrl W
Terminal.InsertInlineCompletion  <-  RIGHT
Terminal.LineDown  <-  ctrl DOWN
Terminal.LineUp  <-  ctrl UP
Terminal.NewTab  <-  shift ctrl T
Terminal.PageDown  <-  shift PAGE_DOWN
Terminal.PageUp  <-  shift PAGE_UP
Terminal.Paste  <-  ctrl V, shift INSERT
Terminal.SearchInCommandHistory  <-  ctrl R
Terminal.SelectBlockAbove  <-  UP, ctrl UP
Terminal.SelectBlockBelow  <-  DOWN
Terminal.SelectLastBlock  <-  ctrl UP
Terminal.SelectPrompt  <-  ctrl DOWN
Terminal.SmartCommandExecution.Debug  <-  shift ctrl ENTER
Terminal.SmartCommandExecution.Run  <-  ctrl ENTER
Terminal.SwitchFocusToEditor  <-  ESCAPE
TextSearchAction  <-  shift ctrl alt E
TodoViewGroupByFlattenPackage  <-  ctrl alt C
TodoViewGroupByShowModules  <-  ctrl alt M
TodoViewGroupByShowPackages  <-  ctrl alt P
ToggleBookmark  <-  F11
ToggleBookmark0  <-  shift ctrl 0
ToggleBookmark1  <-  shift ctrl 1
ToggleBookmark2  <-  shift ctrl 2
ToggleBookmark3  <-  shift ctrl 3
ToggleBookmark4  <-  shift ctrl 4
ToggleBookmark5  <-  shift ctrl 5
ToggleBookmark6  <-  shift ctrl 6
ToggleBookmark7  <-  shift ctrl 7
ToggleBookmark8  <-  shift ctrl 8
ToggleBookmark9  <-  shift ctrl 9
ToggleBookmarkWithMnemonic  <-  ctrl F11
ToggleFindInSelection  <-  ctrl alt E
ToggleRenderedDocPresentation  <-  ctrl alt Q
ToggleTemporaryLineBreakpoint  <-  shift ctrl alt F8
Tree-startEditing  <-  F2
UML.ShowChanges  <-  shift ctrl alt D
Uml.CollapseNodes  <-  C
Uml.ExpandNodes  <-  E
Uml.ShowDiff  <-  shift ctrl D
Unwrap  <-  shift ctrl DELETE
UpdateRunningApplication  <-  ctrl F10
UsageFiltering.Imports  <-  ctrl I
UsageFiltering.ReadAccess  <-  ctrl R
UsageFiltering.WriteAccess  <-  ctrl W
UsageGrouping.Directory  <-  ctrl alt P
UsageGrouping.DirectoryStructure  <-  ctrl alt D
UsageGrouping.FileStructure  <-  ctrl alt F
UsageGrouping.FlattenModules  <-  ctrl alt O
UsageGrouping.Module  <-  ctrl alt M
UsageGrouping.UsageType  <-  ctrl alt T
UsageView.Include  <-  INSERT
Vcs.CombinedDiff.CaretToNextBlock  <-  DOWN, RIGHT, PAGE_DOWN
Vcs.CombinedDiff.CaretToPrevBlock  <-  UP, LEFT, PAGE_UP
Vcs.CombinedDiff.ToggleCollapseBlock  <-  ctrl ESCAPE
Vcs.Log.FocusTextFilter  <-  ctrl L
Vcs.Log.GoToChild  <-  LEFT
Vcs.Log.GoToParent  <-  RIGHT
Vcs.MoveChangedLinesToChangelist  <-  shift alt M
Vcs.Push  <-  shift ctrl K
Vcs.QuickListPopupAction  <-  alt BACK_QUOTE
Vcs.ShowMessageHistory  <-  ctrl M
Vcs.ToggleAmendCommitMode  <-  alt M
VcsHistory.ShowAllAffected  <-  shift alt A
ViewSource  <-  ctrl ENTER
Voice.ActivateVoiceAction  <-  shift alt E
Voice.ReferenceEntityInChatAction  <-  shift alt A
WD.UploadCurrentRemoteFileAction  <-  shift alt Q
WebOpenInAction  <-  alt F2
XDebugger.AttachToProcess  <-  ctrl alt F5
XDebugger.JumpToTypeSource  <-  shift F4
XDebugger.NewWatch  <-  INSERT
XDebugger.SetValue  <-  F2
XPathView.Actions.Evaluate  <-  ctrl alt X , E
XPathView.Actions.FindByExpression  <-  ctrl alt X , F
XPathView.Actions.ShowPath  <-  ctrl alt X , P
ZoomInIdeAction  <-  shift alt EQUALS
ZoomOutIdeAction  <-  shift alt MINUS
com.anthropic.code.plugin.actions.SendToClaudeAction  <-  ctrl alt K
com.github.jk1.ytplugin.commands.OpenCommandWindowAction  <-  shift ctrl Y
com.github.jk1.ytplugin.issues.actions.EditorCreateIssueAction  <-  shift alt K
com.github.jk1.ytplugin.timeTracker.actions.ManualEntryAction  <-  shift ctrl I
com.github.jk1.ytplugin.timeTracker.actions.PauseTrackerAction  <-  shift ctrl P
com.github.jk1.ytplugin.timeTracker.actions.ResetTrackerAction  <-  shift ctrl N
com.github.jk1.ytplugin.timeTracker.actions.ShowAllSavedTimeTrackingItems  <-  shift ctrl O
com.github.jk1.ytplugin.timeTracker.actions.StartTrackerAction  <-  shift ctrl M
com.github.jk1.ytplugin.timeTracker.actions.StopTrackerAction  <-  shift ctrl L
com.jetbrains.php.framework.FrameworkRunConsoleAction  <-  shift ctrl X
com.laravel_idea.plugin.GenerateHelperCodeAction  <-  shift ctrl PERIOD
com.laravel_idea.plugin.LaravelActionChooser  <-  shift ctrl COMMA
context.clear  <-  shift alt X
context.load  <-  shift alt L
context.save  <-  shift alt S
continue.acceptDiff  <-  shift ctrl ENTER
continue.acceptVerticalDiffBlock  <-  shift alt Y
continue.focusContinueInput  <-  ctrl J
continue.focusContinueInputWithoutClear  <-  shift ctrl J
continue.inlineEdit  <-  ctrl I
continue.rejectDiff  <-  shift ctrl BACK_SPACE
continue.rejectVerticalDiffBlock  <-  shift alt N
copilot.chat.inline  <-  shift ctrl G
copilot.chat.show  <-  shift ctrl C
copilot.diffBlock.accept  <-  ctrl Y
copilot.diffBlock.discard  <-  ctrl N
copilot.enableCopilot  <-  shift ctrl alt O
copilot.nes.escape  <-  ESCAPE
copilot.nes.tab  <-  TAB
dev.ott.sops.editor.SopsDecryptAction  <-  ctrl alt D
dev.ott.sops.editor.SopsEncryptAction  <-  ctrl alt E
hg4idea.QFold  <-  shift alt D
hg4idea.QGotoFromPatches  <-  shift alt G
hg4idea.QPushAction  <-  shift alt P
org.intellij.plugins.markdown.ui.actions.styling.InsertImageAction  <-  ctrl U
org.intellij.plugins.markdown.ui.actions.styling.ToggleBoldAction  <-  ctrl B
org.intellij.plugins.markdown.ui.actions.styling.ToggleCodeSpanAction  <-  shift ctrl C
org.intellij.plugins.markdown.ui.actions.styling.ToggleItalicAction  <-  ctrl I
org.intellij.plugins.markdown.ui.actions.styling.ToggleStrikethroughAction  <-  shift ctrl S
sql.SelectInDatabaseView  <-  shift alt B
tasks.close  <-  shift alt W
tasks.goto  <-  shift alt N
tasks.open.in.browser  <-  shift alt B
tasks.switch  <-  shift alt T
```

## Key could not be translated  (0)

_none_

## Mouse shortcuts (not portable to keybindings.json)  (19)

```
Back  <-  mouse: button4
Console.TableResult.GotoReferencedResult  <-  mouse: button1 doubleClick
EditorAddOrRemoveCaret  <-  mouse: alt button1
EditorAddRectangularSelectionOnMouseDrag  <-  mouse: shift alt ctrl button1
EditorCreateRectangularSelection  <-  mouse: shift alt button2
EditorCreateRectangularSelectionOnMouseDrag  <-  mouse: button2
EditorCreateRectangularSelectionOnMouseDrag  <-  mouse: shift alt button1
EditorPasteFromX11  <-  mouse: button2
Forward  <-  mouse: button5
Git.Log.Branches.Change.Branch.Filter  <-  mouse: button1 doubleClick
GotoDeclaration  <-  mouse: button2
GotoDeclaration  <-  mouse: ctrl button1
GotoImplementation  <-  mouse: alt ctrl button1
GotoTypeDeclaration  <-  mouse: shift ctrl button1
OpenInRightSplit  <-  mouse: alt button1 doubleClick
QuickEvaluateExpression  <-  mouse: shift alt button1
QuickJavaDoc  <-  mouse: alt button2
Rainbow.ScopeHighlightingAction  <-  mouse: ctrl button3
Rainbow.ScopeOutsideHighlightingRestrainAction  <-  mouse: alt button3
```
