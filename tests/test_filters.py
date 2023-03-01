from boilerpy3.document import DefaultLabels, TextBlock, TextDocument
from boilerpy3.filters import (
    AddPrecedingLabelsFilter,
    ArticleMetadataFilter,
    BlockProximityFusion,
    BoilerplateBlockFilter,
    CanolaFilter,
    ContentFusion,
    DensityRulesClassifier,
    DocumentTitleMatchClassifier,
    ExpandTitleToContentFilter,
    IgnoreBlocksAfterContentFilter,
    IgnoreBlocksAfterContentFromEndFilter,
    InvertedFilter,
    KeepLargestBlockFilter,
    KeepLargestFulltextBlockFilter,
    LabelFusion,
    LabelToBoilerplateFilter,
    LabelToContentFilter,
    MarkEverythingContentFilter,
    MinClauseWordsFilter,
    MinFulltextWordsFilter,
    MinWordsFilter,
    NumWordsRulesClassifier,
    SimpleBlockFusionProcessor,
    SplitParagraphBlocksFilter,
    SurroundingToContentFilter,
    TerminatingBlocksFinder,
)

default_words = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec fermentum tincidunt magna, eu "
    "pulvinar mauris dapibus pharetra. In varius, nisl a rutrum porta, sem sem semper lacus, "
    "et varius urna tellus vel lorem. Nullam urna eros, luctus eget blandit ac, imperdiet "
    "feugiat ipsum. Donec laoreet tristique mi a bibendum. Sed pretium bibendum scelerisque. "
    "Mauris id pellentesque turpis. Mauris porta adipiscing massa, quis tempus dui pharetra ac. "
    "Morbi lacus mauris, feugiat ac tempor ut, congue tincidunt risus. Pellentesque tincidunt "
    "adipiscing elit, in fringilla enim scelerisque vel. Nulla facilisi. ".split(" ")
)


def make_doc(words_arr, num_anchor_words_arr=None, is_content_arr=None, label_arr=None):
    text_blocks = []
    for idx, words in enumerate(words_arr):
        if isinstance(words, int):
            num_words = words
            text = " ".join(default_words[:num_words])
        else:
            text = words
            num_words = text.count(" ")
        try:
            num_anchor_words = num_anchor_words_arr[idx]
        except (TypeError, IndexError):
            num_anchor_words = 0
        block = TextBlock(text, set(), num_words, num_anchor_words, 0, 0, idx)
        try:
            block.is_content = is_content_arr[idx]
        except (TypeError, IndexError):
            pass
        try:
            label = label_arr[idx]
            if label is None:
                pass
            elif isinstance(label, list):
                for l in label:
                    block.add_label(l)
            else:
                block.add_label(label)
        except (TypeError, IndexError):
            pass

        text_blocks.append(block)

    return TextDocument(text_blocks)


def verify_content(filtr, doc, content_arr, show=False):
    is_content_before = [block.is_content for block in doc.text_blocks]
    is_changed = filtr.process(doc)
    is_content = [block.is_content for block in doc.text_blocks]
    assert is_content == content_arr
    assert is_changed == (is_content != is_content_before)


def test_MarkEverythingContentFilter():
    doc = make_doc([5, 100, 80], None, [False, True, False])
    verify_content(MarkEverythingContentFilter(), doc, [True, True, True])


def test_InvertedFilter():
    doc = make_doc([5, 100, 80], None, [False, True, False])
    verify_content(InvertedFilter(), doc, [True, False, True])


def test_BoilerplateBlockFilter():
    # keeps if is_content
    doc = make_doc([5, 100, 10, 50, 80], None, [False, True, False, True, False])
    init_blocks = doc.text_blocks
    final_blocks = [init_blocks[1], init_blocks[3]]
    filtr = BoilerplateBlockFilter()
    is_changed = filtr.process(doc)
    is_content = [block.is_content for block in doc.text_blocks]
    assert doc.text_blocks == final_blocks
    assert is_content == [True, True]
    assert is_changed is True


def test_MinWordsFilter():
    # rejects if #words<k
    doc = make_doc([10, 50], None, [True, True])
    verify_content(MinWordsFilter(20), doc, [False, True])


def test_MinClauseWordsFilter():
    # reject block if max(#words for each clause in block)<k
    doc = make_doc(
        [
            "This is a clause, because it is separated by a comma.",
            "Real short",
            "Lots of, very, very, very, small, clauses.",
            "If acceptClausesWithoutDelimiter is false then clauses that dont end in punctuation dont count",
        ],
        None,
        [True, True, True, True],
    )
    verify_content(MinClauseWordsFilter(5, False), doc, [True, False, False, False])


def test_SplitParagraphBlocksFilter():
    # split paragraphs intpo separate blocks
    doc = make_doc(
        ["A single paragraph.", "Multiple paragraphs.\n\nParagraph 2 is here."],
        None,
        [True, False],
    )
    filtr = SplitParagraphBlocksFilter()
    is_changed = filtr.process(doc)
    text_arr = [block.text for block in doc.text_blocks]
    is_content = [block.is_content for block in doc.text_blocks]
    assert text_arr == [
        "A single paragraph.",
        "Multiple paragraphs.",
        "Paragraph 2 is here.",
    ]
    assert is_content == [True, False, False]
    assert is_changed is True


def test_SurroundingToContentFilter():
    # accept block if prev and next blocks are content and condition is met
    doc = make_doc(
        [10, 20, 10, 5, 10, 20, 20, 10],
        [0, 0, 0, 5, 0, 0, 0, 0],
        [True, False, True, False, True, False, False, True],
    )
    default_condition = lambda tb: tb.link_density == 0 and tb.num_words > 6
    verify_content(
        SurroundingToContentFilter(default_condition),
        doc,
        [True, True, True, False, True, False, False, True],
    )


def test_LabelToBoilerplateFilter():
    # reject block if it has a particular label
    lb_not = DefaultLabels.STRICTLY_NOT_CONTENT
    lb_maybe = DefaultLabels.MIGHT_BE_CONTENT
    doc = make_doc(
        [10, 10, 10, 10],
        None,
        [True, True, True, True],
        [lb_not, lb_maybe, [lb_not, lb_maybe], None],
    )
    verify_content(
        LabelToBoilerplateFilter(DefaultLabels.STRICTLY_NOT_CONTENT),
        doc,
        [False, True, False, True],
    )


def test_LabelToContentFilter():
    # accept block if it has a particular label
    lb_not = DefaultLabels.STRICTLY_NOT_CONTENT
    lb_maybe = DefaultLabels.MIGHT_BE_CONTENT
    doc = make_doc(
        [10, 10, 10, 10],
        None,
        [False, False, False, False],
        [lb_not, lb_maybe, [lb_not, lb_maybe], None],
    )
    verify_content(
        LabelToContentFilter(DefaultLabels.MIGHT_BE_CONTENT),
        doc,
        [False, True, True, False],
    )


def test_SimpleBlockFusionProcessor():
    # join blocks with the same number of words per line
    doc = make_doc(
        ["two words", "three fucking words", "another three words"],
        None,
        [False, False, False],
    )
    filtr = SimpleBlockFusionProcessor()
    is_changed = filtr.process(doc)
    block_idxs = [
        (block.offset_blocks_start, block.offset_blocks_end)
        for block in doc.text_blocks
    ]
    assert block_idxs == [(0, 0), (1, 2)]
    assert is_changed is True


def test_ContentFusion():
    # join blocks with low link density
    filtr = ContentFusion()

    # merge
    doc = make_doc([10, 10], [0, 0], [True, False])
    is_changed = filtr.process(doc)
    assert len(doc.text_blocks) == 1
    assert is_changed is True

    # dont merge if tagged not content
    doc = make_doc(
        [10, 10], [0, 0], [True, False], [None, DefaultLabels.STRICTLY_NOT_CONTENT]
    )
    is_changed = filtr.process(doc)
    assert len(doc.text_blocks) == 2
    assert is_changed is False

    # dont merge if link density is high
    doc = make_doc([10, 10], [0, 8], [True, False])
    is_changed = filtr.process(doc)
    assert len(doc.text_blocks) == 2
    assert is_changed is False

    # multiple pass merging
    doc = make_doc([10, 10, 10, 10], [0, 0, 0, 0], [True, False, True, False])
    is_changed = filtr.process(doc)
    assert len(doc.text_blocks) == 1
    assert is_changed is True


def test_LabelFusion():
    # fuse blocks with identical labels - ONLY LOOKS AT LABELS with markup prefix

    lb1 = DefaultLabels.MARKUP_PREFIX + ".title"
    lb2 = DefaultLabels.MARKUP_PREFIX + ".menu"
    doc = make_doc(
        [10, 10, 10, 10, 10, 10, 10],
        None,
        None,
        [None, None, lb1, lb1, lb2, lb2, [lb1, lb2]],
    )
    filtr = LabelFusion()
    is_changed = filtr.process(doc)
    block_idxs = [
        (block.offset_blocks_start, block.offset_blocks_end)
        for block in doc.text_blocks
    ]
    assert block_idxs == [(0, 1), (2, 3), (4, 5), (6, 6)]
    assert is_changed is True


def test_BlockProximityFusion():
    # fuse blocks close to each other
    doc = make_doc(
        [10, 10, 10, 10, 10, 10, 10], None, [False, True, True, True, True, True, False]
    )
    filtr = BlockProximityFusion(1, True, False)
    is_changed = filtr.process(doc)
    block_idxs = [
        (block.offset_blocks_start, block.offset_blocks_end)
        for block in doc.text_blocks
    ]
    assert block_idxs == [(0, 0), (1, 5), (6, 6)]
    assert is_changed is True


def test_ExpandTitleToContentFilter():
    # marks all between title and content start
    lb1 = DefaultLabels.MIGHT_BE_CONTENT
    doc = make_doc(
        [10, 10, 10, 10],
        None,
        [False, False, False, True],
        [lb1, [lb1, DefaultLabels.TITLE], lb1, lb1],
    )
    verify_content(ExpandTitleToContentFilter(), doc, [False, True, True, True])


def test_articleMetadata():
    # marks as content and tags blocks with date/time data
    doc = make_doc(
        [
            " May 1, 2009 8:00pm EST",
            "May not be date 1",
            "By Frank Sinatra",
            "By looking at this sentence, you can see there is no author",
        ],
        None,
        [False, False, False, False],
    )
    verify_content(ArticleMetadataFilter(), doc, [True, False, True, False])
    labels = [block.labels for block in doc.text_blocks]
    assert DefaultLabels.ARTICLE_METADATA in labels[0]


def test_largestBlock():
    # accept largest block and reject all others
    doc = make_doc([10, 10, 50, 10], None, [False, True, True, True])
    verify_content(KeepLargestBlockFilter(), doc, [False, False, True, False])


def test_addPrecedingLabels():
    # add prefix+preceding label to each block
    lb1 = DefaultLabels.TITLE
    lb2 = DefaultLabels.MIGHT_BE_CONTENT
    prefix = "^"
    doc = make_doc([10, 10, 10], None, None, [lb1, lb2, None])
    filtr = AddPrecedingLabelsFilter(prefix)
    is_changed = filtr.process(doc)
    labels = [block.labels for block in doc.text_blocks]
    assert labels == [{lb1}, {prefix + lb1, lb2}, {prefix + lb2}]
    assert is_changed is True


def test_documentTitleMatch():
    # add title label to blocks matching sections of the title
    doc = make_doc(["News", "This is the real title", "Red herring"])
    doc.title = "News - This is the real title"
    filtr = DocumentTitleMatchClassifier(None, True)
    is_changed = filtr.process(doc)
    labels = [block.labels for block in doc.text_blocks]
    assert labels == [set(), {DefaultLabels.TITLE}, set()]
    assert is_changed is True


def test_minFulltextWords():
    # choose largest block
    doc = make_doc([10, 50], None, [True, True])
    verify_content(MinFulltextWordsFilter(30), doc, [False, True])


def test_largestFulltextBlock():
    # accept largest block that has been marked as content and reject all others
    doc = make_doc([10, 50, 80, 10], None, [True, True, False, False])
    verify_content(KeepLargestFulltextBlockFilter(), doc, [False, True, False, False])


def test_ignoreBlocksAfterContent():
    # rejects all blocks after(&including) first block with ENDOFTEXT label
    # Also: ENDOFTEXT labels are ignored until the total number of words in content blocks reaches a certain number
    lb = DefaultLabels.INDICATES_END_OF_TEXT
    doc = make_doc(
        [10, 30, 50, 80, 20],
        None,
        [False, True, True, True, True],
        [lb, None, None, lb, None],
    )
    verify_content(
        IgnoreBlocksAfterContentFilter(60), doc, [False, True, True, False, False]
    )


def test_ignoreBlocksAfterContentFromEnd():
    # rejects all blocks with ENDOFTEXT label
    # works backwards until the total number of words in content blocks reaches 200 and then halts
    lb = DefaultLabels.INDICATES_END_OF_TEXT
    doc = make_doc(
        [80, 80, 80, 80, 80],
        None,
        [True, True, True, True, True],
        [lb, None, None, lb, None],
    )
    verify_content(
        IgnoreBlocksAfterContentFromEndFilter(), doc, [True, True, True, False, True]
    )


def test_terminatingBlocks():
    # add ENDOFTEXT label at detected beginning of comments section
    lb = DefaultLabels.INDICATES_END_OF_TEXT
    s1 = "Comments can be the first word of article text.  If there are many words in the block, it is not comments"
    s2 = "Thanks for your comments - this feedback is now closed"
    doc = make_doc(["Comments", "Please have your say", "48 Comments today", s1, s2])
    filtr = TerminatingBlocksFinder()
    is_changed = filtr.process(doc)
    has_label = [(lb in block.labels) for block in doc.text_blocks]
    assert has_label == [True, True, True, False, True]
    assert is_changed is True


def test_numWordsClassifier():
    # accepts or rejects block based on machine-trained decision tree rules
    # using features from previous, current and next block
    filtr = NumWordsRulesClassifier()

    doc = make_doc([2, 10, 10], [0, 0, 0], [True, True, True])
    filtr.process(doc)
    # test middle block only
    assert doc.text_blocks[1].is_content is False

    doc = make_doc([10, 10, 10], [0, 0, 0], [True, True, True])
    filtr.process(doc)
    assert doc.text_blocks[1].is_content is True


def test_densityClassifier():
    # accepts or rejects block based on a different set of machine-trained decision tree rules
    # using features from previous, current and next block
    doc = make_doc([10, 10, 5], [10, 0, 0], [True, True, True])
    DensityRulesClassifier().process(doc)
    assert doc.text_blocks[1].is_content is False


def test_canolaClassifier():
    # accepts or rejects block based on a different set of machine-trained decision tree rules
    # using features from previous, current and next block
    doc = make_doc([5, 10, 30], [5, 10, 0], [True, False, True])
    CanolaFilter().process(doc)
    assert doc.text_blocks[1].is_content is True
