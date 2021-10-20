import os
from boilerpy3.document import DefaultLabels, TextBlock
from boilerpy3.extractors import ArticleExtractor, Extractor

TEST_FILE = os.path.join(os.path.dirname(__file__), "test.html")

extractor = Extractor(None)
default_words = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec fermentum tincidunt magna, eu " \
                "pulvinar mauris dapibus pharetra. In varius, nisl a rutrum porta, sem sem semper lacus, et varius " \
                "urna tellus vel lorem. Nullam urna eros, luctus eget blandit ac, imperdiet feugiat ipsum. Donec " \
                "laoreet tristique mi a bibendum. Sed pretium bibendum scelerisque. Mauris id pellentesque turpis. " \
                "Mauris porta adipiscing massa, quis tempus dui pharetra ac. Morbi lacus mauris, feugiat ac tempor " \
                "ut, congue tincidunt risus. Pellentesque tincidunt adipiscing elit, in fringilla enim scelerisque " \
                "vel. Nulla facilisi. ".split(' ')


def content_item(s):
    if isinstance(s, int):
        return ' '.join(default_words[:s])
    else:
        return s


def make_content(str_arr):
    return [content_item(s) for s in str_arr]


def make_doc_2(template, content_arr):
    template_arr = template.split('*')
    s = ""
    for i, j in zip(template_arr[:-1], content_arr):
        s += i + j
    s += template_arr[-1]
    doc = extractor.parse_doc(s)
    return doc


def test_blocks():
    template = "<html><body><p>*</p><div>*<p>*</p>*</div></body></html>"
    content = make_content([4, 5, 6, 7])
    doc = make_doc_2(template, content)
    
    blocks = doc.text_blocks
    text_arr = [block.text for block in blocks]
    num_words = [block.num_words for block in blocks]
    assert text_arr == content
    assert num_words == [4, 5, 6, 7]


def test_anchor():
    template = "<html><body><p>*</p><div>*<a href='half.html'>*</a></div><a href='full.html'><p>*</p></a></body></html>"
    content = make_content([6, "end with space ", 3, 6])
    doc = make_doc_2(template, content)
    
    blocks = doc.text_blocks
    text_arr = [block.text for block in blocks]
    density_arr = [block.link_density for block in blocks]
    num_anchor_words = [block.num_words_in_anchor_text for block in blocks]
    assert text_arr == [content[0], content[1] + content[2], content[3]]
    assert num_anchor_words == [0, 3, 6]
    assert density_arr == [0.0, 0.5, 1.0]


def test_title():
    title_text = "THIS IS TITLE"
    s = "<html><head><title>" + title_text + "</title></head><body><p>THIS IS CONTENT</p></body></html>"
    doc = extractor.parse_doc(s)
    assert doc.title == title_text


def test_body():
    body_text = "THIS IS CONTENT"
    s = "<html><head><p>NOT IN BODY</p></head><body><p>" + body_text + "</p></body></html>"
    doc = extractor.parse_doc(s)
    text_arr = [block.text for block in doc.text_blocks]
    assert text_arr == [body_text]


def test_inline():
    template = "<html><body><div><h1>*</h1><h4>*</h4></div><div><span>*</span><b>*</b></div></body></html>"
    content = ['AA', 'BB', 'CC', 'DD']
    doc = make_doc_2(template, content)
    
    blocks = doc.text_blocks
    text_arr = [block.text for block in blocks]
    assert text_arr == [content[0], content[1], content[2] + content[3]]


def test_ignorable():
    template = "<html><body><p>*</p><option><p>*</p></option></body></html>"
    content = make_content([10, 12])
    doc = make_doc_2(template, content)
    
    blocks = doc.text_blocks
    text_arr = [block.text for block in blocks]
    assert text_arr == [content[0]]


def assert_range(val, minval, maxval):
    assert minval <= val <= maxval


def test_textDensity():
    template = "<html><body><p>*</p><p>*</p></body></html>"
    content = make_content([80, "one, !!! two"])
    doc = make_doc_2(template, content)
    
    blocks = doc.text_blocks
    num_arr = [[block.num_words, block.num_words_in_wrapped_lines, block.num_wrapped_lines, block.text_density] for
               block in blocks]
    
    # exact values are unknown, approximate value range to check
    assert blocks[0].num_words == 80
    assert_range(blocks[0].num_words_in_wrapped_lines, 60, 80)
    assert_range(blocks[0].num_wrapped_lines, 4, 7)
    assert_range(blocks[0].text_density, 8, 16)
    
    assert num_arr[1] == [2, 2, 1, 2]


def test_block_idxs():
    template = "<html><body><p>*  </p>  <p> * </p><p>*  </p><p>*  </p></body></html>"
    content = make_content([11, 12, 13, 14])
    doc = make_doc_2(template, content)
    
    blocks = doc.text_blocks
    idx_arr = [[block.offset_blocks_start, block.offset_blocks_end] for block in blocks]
    assert idx_arr == [[0, 0], [1, 1], [2, 2], [3, 3]]


def test_tag_level():
    template = "<html><body><div><p><span><a href='x.html'>*</a></span></p>*</div></body></html>"
    content = make_content([5, 6])
    doc = make_doc_2(template, content)
    
    blocks = doc.text_blocks
    level_arr = [block.tag_level for block in blocks]
    assert level_arr == [5, 3]


def test_merge():
    block1 = TextBlock("AA BB CC ", {0}, 3, 3, 3, 1, 0)
    block2 = TextBlock("DD EE FF GG HH II JJ .", {1}, 6, 0, 6, 2, 1)
    block1.add_labels(DefaultLabels.MIGHT_BE_CONTENT)
    block2.add_labels(DefaultLabels.ARTICLE_METADATA)
    block1.merge_next(block2)
    assert block1.text == "AA BB CC \nDD EE FF GG HH II JJ ."
    assert block1.num_words == 9
    assert block1.num_words_in_anchor_text == 3
    assert round(abs(block1.link_density - 1.0 / 3.0), 7) == 0
    assert block1.text_density == 3
    assert block1.labels == {DefaultLabels.MIGHT_BE_CONTENT, DefaultLabels.ARTICLE_METADATA}
    assert block1.offset_blocks_start == 0
    assert block1.offset_blocks_end == 1


def test_extraction():
    expected = """
Learn Kubernetes Basics
Kubernetes (K8s) is an open-source system for
                automating deployment, scaling, and management of containerized applications.
It groups containers that make up an application into logical units for easy management and
                    discovery. Kubernetes builds upon 15 years of experience of running production
                        workloads at Google , combined with best-of-breed ideas and practices from the community.
Planet Scale
Designed on the same principles that allows Google to run billions of containers a week, Kubernetes
                    can scale without increasing your ops team.
Never Outgrow
Whether testing locally or running a global enterprise, Kubernetes flexibility grows with you to
                    deliver your applications consistently and easily no matter how complex your need is.
Run Anywhere
Kubernetes is open source giving you the freedom to take advantage of on-premises, hybrid, or public
                    cloud infrastructure, letting you effortlessly move workloads to where it matters to you.
The Challenges of Migrating 150+ Microservices to Kubernetes
By Sarah Wells, Technical Director for Operations and Reliability, Financial Times
Watch Video
    """
    
    with open(TEST_FILE) as html_file:
        html = html_file.read()
    extractor = ArticleExtractor()
    extracted_text = extractor.get_content(html)
    assert expected.strip() == extracted_text.strip()
