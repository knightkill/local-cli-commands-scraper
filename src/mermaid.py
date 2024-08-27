import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import subprocess
from langchain_core.pydantic_v1 import BaseModel, Field
import os

# Initialize the LLM
#llm = ChatOpenAI(model="ft:gpt-4o-mini-2024-07-18:anormaly-labs::9yzZga4Z")
llm = ChatOpenAI(model="ft:gpt-4o-mini-2024-07-18:anormaly-labs::9zdIrrcb")


class ProcessPrompt(BaseModel):
    prompt: str = Field(description="Prompt to generate Mermaid code for a process or system.")


def generate_mermaid_code(text_section):
    # Create a prompt template for generating Mermaid code
    prompt_template = """
    {text_section}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Convert the following instruction into a detailed Mermaid diagram in Markdown format. The diagram "
                   "type (flowchart, sequence, class, etc.) should be determined contextually based on the "
                   "instruction content. Ensure that all relevant details, relationships, decision points, "
                   "and interactions are represented clearly and accurately. The output should be solely the Mermaid "
                   "diagram code, without any extra information, explanations, or formatting beyond what is required "
                   "for the diagram itself."),
        ("human", "{text_section}"),
    ])
    input_data = {
        "text_section": text_section,
    }

    chain = (
            prompt
            | llm
            | StrOutputParser()
    )

    mermaid_code = chain.invoke(input_data)
    return mermaid_code.strip()


# Make random prompt that will be used to generate the Mermaid code
def generate_mermaid_prompt():
    mini_llm = ChatOpenAI(model="gpt-4o-mini")
    mini_llm.with_structured_output(ProcessPrompt, method="json_mode")
    # Create a prompt template for generating Mermaid code
    prompt_template = """Generate a detailed description of a process or system related to the given topic in a first-person perspective. The process should involve multiple steps, decisions, and interactions between components. It should cover the flow of actions, possible conditions, and outcomes, and should be structured in a way that can be represented using sub-diagrams or sub-graphs with or without interconnections. The description should be detailed enough to allow the creation of a complex flowchart or diagram using these sub-sections. Ensure that only the process description is provided, without any additional information. Use the topic below:

Topic: Programming"""

    #prompt = ChatPromptTemplate.from_template(prompt_template)
    #chain = (
    #        prompt
    #        | mini_llm
    #        | StrOutputParser()
    #)

    mermaid_code = mini_llm.invoke(prompt_template)
    print(mermaid_code)
    return mermaid_code.content


def convert_mermaid_to_image(mermaid_code):
    # Save the Mermaid code to a temporary markdown file
    #prefix = "```mermaid\n"
    #suffix = "\n```"
    mermaid_file = "./output/diagram.mmd"
    with open(mermaid_file, "w") as f:
        #f.write(prefix + mermaid_code + suffix)
        f.write(mermaid_code)

    # Use Mermaid CLI to convert the markdown to an image
    output_file = "./output/diagram-1.png"
    try:
        response = subprocess.run(
            ["mmdc", "-i", mermaid_file, "-o", output_file, "--theme", "dark"],
            check=True,
        )
        return output_file
    except subprocess.CalledProcessError as e:
        st.error("Failed to generate the diagram image.")
        st.error(str(e))
        return None


def main():
    st.title("Mermaid Diagram Generator")

    if 'prompt' not in st.session_state:
        st.session_state.prompt = """I am a coffee brewing system that operates in a few distinct steps. First, 
        I start by gathering all the necessary ingredients: fresh coffee beans, water, and a coffee filter. Once I 
        have everything ready, I begin with the grinding process, where I grind the coffee beans to a medium 
        consistency. After the beans are ground, I move on to the brewing stage. I measure the correct amount of 
        water and heat it to the optimal temperature of about 200°F (93°C). Once the water is ready, I pour it over 
        the ground coffee in the filter, allowing the water to extract the flavors as it drips into the carafe below. 
        Finally, after brewing for about four to five minutes, I have a fresh pot of coffee ready to serve. I can 
        then pour the coffee into a cup and add milk or sugar according to preference."""

    if st.button("Generate Random Prompt"):
        st.session_state.prompt = generate_mermaid_prompt()

    text_section = st.text_area("Text Section to Describe", value=st.session_state.prompt, key="prompt")

    if st.button("Generate Mermaid Diagram"):
        with st.spinner("Generating Mermaid code..."):
            mermaid_code = generate_mermaid_code(st.session_state.prompt)
            st.code(mermaid_code, language="mermaid")

            st.write("Converting Mermaid code to image using Mermaid CLI...")
            image_path = convert_mermaid_to_image(mermaid_code)

            if image_path:
                st.image(image_path, caption="Generated Mermaid Diagram")


if __name__ == "__main__":
    main()
