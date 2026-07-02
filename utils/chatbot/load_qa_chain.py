from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def RetrievalQAChain(llm, prompt, db, query, retriever):
    retriever_runnable = RunnableLambda(
        lambda question: {
            "context": format_docs(retriever.get_relevant_documents(question)),
            "question": question,
        }
    )

    chain = retriever_runnable | prompt | llm | StrOutputParser()
    return chain
