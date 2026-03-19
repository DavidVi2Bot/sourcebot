# sourcebot/context/skill/skill_summary.py

from xml.etree.ElementTree import Element, SubElement, tostring
from typing import List
from sourcebot.context.skill.skill import Skill
from sourcebot.context.skill.skill_requirements import check_requirements, missing_requirements

class SkillSummary:
    """Generate XML summary of a list of skills."""
    
    @staticmethod
    def generate(skills: List[Skill], pretty: bool = False) -> str:
        root = Element("skills")
        for skill in skills:
            skill_elem = SubElement(root, "skill")
            available = check_requirements(skill)
            skill_elem.set("available", str(available).lower())
            SubElement(skill_elem, "name").text = skill.name
            SubElement(skill_elem, "description").text = skill.description
            SubElement(skill_elem, "location").text = skill.source
            if not available:
                reqs = missing_requirements(skill)
                if reqs:
                    SubElement(skill_elem, "requires").text = reqs
        xml_bytes = tostring(root, encoding="unicode")
        if pretty:
            import xml.dom.minidom
            dom = xml.dom.minidom.parseString(xml_bytes)
            return dom.toprettyxml(indent="  ")
        
        return xml_bytes