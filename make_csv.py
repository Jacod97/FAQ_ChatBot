import pandas as pd
import pickle

with open('./data/final_result.pkl', 'rb') as f:
    data = pickle.load(f)
type(data)

df_dict = {
    "q_type" : [],
    "question" : [],
    "answer" : [],
    "keyword" : []
}

for i in range(len(data)):
    questions = list(data.keys())[i]
    answers = list(data.values())[i].split("\n")
    answers = [i for i in answers if i != ""]
    if questions[0] == "[":
        q1 = questions.find("[")
        q2 = questions.find("]")
        df_dict['q_type'].append(questions[q1:q2+1])
    else:
        df_dict['q_type'].append(None)

    if "관련 도움말/키워드" in answers:
        start = answers.index("관련 도움말/키워드")
        end = answers.index("도움말 닫기")
        keywords = answers[start+1:end]
    else:
        keywords = None

    df_dict['question'].append(questions[q2+1:])
    df_dict['answer'].append(answers[0])
    df_dict['keyword'].append(keywords)

df = pd.DataFrame(df_dict)
df.to_csv("./data/faq.csv", index=False, encoding="utf-8")
