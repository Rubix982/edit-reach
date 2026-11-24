# C-011 · The six predictions, written before any count was read

_2026-11-24 · read off Cohen et al., TACL 2024 (arXiv 2307.12976), §3, via the arXiv HTML. No count had been looked at when this file was written._

For each type: does the benchmark's own definition say the test query is about the edited subject `e` itself, or about some other entity? A query about `e` should contain `e`'s surface name; one about another entity should not.

| released key | the paper's criterion | the query is about | predicted strict rate |
| --- | --- | --- | --- |
| `Compositionality_I` | Compositionality I — *"compose the edited fact with other facts about the target object"* | `e` | **high** |
| `Relation_Specificity` | Relation Specificity — *"facts about e, with relations whose objects are not influenced by o"* | `e` | **high** |
| `Forgetfulness` | *inferred* to be Preservation — *"adding a new object should not affect the other objects encoded about e"*, whose example phrasing is *"The award received by ⟨e⟩ which is not ⟨o*⟩ is"* | `e` | **high** |
| `Logical_Generalization` | Logical Generalization — queries about `x ∈ {e, o, o*}` | mixed | **intermediate**, below Compositionality I and above Compositionality II |
| `Subject_Aliasing` | Subject Aliasing — *"other entities e′ that are aliases of e"* | an alias of `e` | **low on strict, high once variants count** |
| `Compositionality_II` | Compositionality II — *"compose the edited fact with facts about a different subject"*, a different entity `e′ ≠ e` that has `e` as its object | `e′` | **near zero** |

**One name does not match and the mismatch is recorded rather than assumed away.** The paper's sixth criterion is **Preservation**; the released files carry **`Forgetfulness`** and no `Preservation`. The row above treats them as the same criterion under two names, on the evidence of the example phrasing only. If the `Forgetfulness` prompts do not carry that *"which is not"* shape, the inference is wrong and the row is void.

**What would make the whole table wrong.** If a type predicted *high* comes out low, the adapter is recovering a string that does not belong in that type's prompts. If a type predicted *near zero* comes out high, the screen is matching something that is not the edited subject.
