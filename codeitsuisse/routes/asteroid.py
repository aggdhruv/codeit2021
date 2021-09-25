import logging
import json

from flask import request, jsonify

from codeitsuisse import app

logger = logging.getLogger(__name__)\

def asteroid_calc(text):
    print(text)
    print(len(text))
    max_score = 0
    origin = 0
    for index,i in enumerate(text):
        score = 0
        count = 1
        cur_left_index = index -1
        cur_right_index = index
        if(index == 0 or index == len(text)-1):
            score = 1
        else:
            while(cur_right_index!=len(text)-1 and cur_left_index!=0):
                j = 0
                k = 0
                left_count = 0
                right_count = 0
                print('Right ' + text[cur_right_index+1::])
                for j in range(len(text[cur_right_index+1::])):
                    if text[j+cur_right_index+1]==text[cur_right_index]:
                        print(text[j+cur_right_index+1], end=' ')
                        right_count += 1
                    else:
                        break
                print()
                print('Left ' + text[cur_left_index::-1])
                for k in range(len(text[cur_left_index::-1])):
                    if text[cur_left_index-k]==text[cur_left_index]:
                        print(text[cur_left_index-k], end=' ')
                        left_count += 1
                    else:
                        break
                print()
                sum = count+left_count+right_count
                if sum<=6:
                    score += sum
                elif sum <=9:
                    score += sum*1.5
                else:
                    score += sum*2
                print(score)
                if(left_count == 0 or right_count ==0):
                    break
                count = 1
                cur_left_index = cur_left_index-k
                cur_right_index = j+cur_right_index+1
        if(score>= max_score):
            max_score = score
            origin = index
        # print()
        print('Index: ' + str(index), end=" ")
        print('Score: '+ str(score))
        print()
        # print()
    print()
    print('Origin: ' + str(origin), end=' ')
    print('Max Score: ' + str(max_score))
    return max_score,origin
        

@app.route('/asteroid', methods=['POST'])
def evaluateAsteroid():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    result=[]
    for i in data["test_cases"]:
        score, origin = asteroid_calc(i)
        a_result = dict({'input':i,'score':score,'origin':origin})
        result.append(a_result)
    return jsonify(result)