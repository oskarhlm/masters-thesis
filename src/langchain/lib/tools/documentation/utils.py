import lxml.etree as le
import os
import fnmatch


def find_files(root_folder, extensions):
    matches = []
    for root, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if any(fnmatch.fnmatch(filename, f'*.{ext}') for ext in extensions):
                matches.append(os.path.join(root, filename))
    return matches


def get_docs_paths():
    root_folder = '/home/dev/master-thesis/data'
    docs_extensions = ['xsd', 'pdf']
    files = find_files(root_folder, docs_extensions)
    formatted_list = "\n".join([f"- {file}" for file in files])
    return formatted_list


def clean_xml_docs(path: str) -> str:
    def remove_all_tags(tag_name: str, doc):
        tags = doc.findall(f'.//{{*}}{tag_name}')
        for elem in tags:
            parent = elem.getparent()
            parent.remove(elem)

    def remove_attributes_except(element, allowed_attributes):
        all_attributes = list(element.attrib.keys())
        for attribute in all_attributes:
            if attribute not in allowed_attributes:
                del element.attrib[attribute]

    def add_documentation_to_parent(doc):
        for annotation in doc.findall(".//{*}annotation"):
            documentation = annotation.find(".//{*}documentation")
            if documentation is not None:
                description_text = documentation.text
                parent_element = annotation.getparent()
                new_documentation = le.Element("documentation")
                new_documentation.text = description_text
                parent_element.insert(0, new_documentation)
            parent_element.remove(annotation)

    path = '/home/dev/master-thesis/data/bygning/bygningspunkt_docs.xsd'

    with open(path, 'r', encoding='utf-8') as f:
        doc = le.parse(f)

    remove_tags = ['appinfo', 'import', 'attributeGroup']
    for tag in remove_tags:
        remove_all_tags(tag, doc)

    allowed_attributes = ['name', 'value', 'ref']

    for element in doc.iter():
        remove_attributes_except(element, allowed_attributes)

    add_documentation_to_parent(doc)

    return le.tostring(doc.getroot(), pretty_print=True,
                       encoding='utf-8').decode("utf-8")
