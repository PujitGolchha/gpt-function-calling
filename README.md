# Thesis

Repository of the thesis, submitted by Pujit Golchha to the Data and Web Science Group as the final requirement for obtaining the Master's degree in Data Science at the University of Mannheim. This thesis was supervised by Prof Dr. Christian Bizer between September 2023 and February 2024.

# About the thesis (Summary)

In this thesis, the primary objective was to evaluate and understand the novel function-calling capability of GPT. To accomplish this, we first picked out two diverse domains namely Music and Geo, and created custom APIs, leveraging widely available open-source data and pre-existing APIs. For the Music Domain, our API is a more structured and filtered version of the MusicBrainz API and Spotify API. For the Geo Domain, our API is mainly based on data from Open Street Maps and DBpedia.  

Subsequently, we framed multiple question sets for each domain, with each question set uniquely designed in a way to evaluate particular aspects of this capability. This led to the formulation of 111 questions, spanning 6 different objectives in each domain.  Additionally, we devised different prompt setups aimed not only at testing GPT's capability but also to help enhance its performance, for example, the Few-Shot COT prompt setup for both domains. 
Experiments were then conducted on each question across a variety of setups. These setups included using different prompts, restricting access to distinct subsets of functions, as well as using function descriptions of different modalities. By systematically varying these experimental parameters, we aimed to gain deeper insights into how GPT responds to different input conditions.

The experimental results show that for the less complex tasks, such as the Single Function Call and Extra Context questions, GPT successfully passes the Minimum Functionality Test and Invariance Test criteria. The combined average accuracy for both question sets is 85\%. For these question sets it can perform well even with the simplest prompt and access to functions with basic descriptions. Additionally, it also performs well on Common Knowledge questions, however avoiding redundant calls is not its strength. Even though there is a drop in the API calls using the Cost Awareness Prompt, there are still questions for which it makes function calls with the answer itself as a parameter. For more intricate tasks i.e. Reasoning and Multiple Function questions, prompting with Few-Shot CoT and giving it access to functions with good refined descriptions guarantees the best performance. Nevertheless, there remains room for improvement as even with Few-Shot CoT, it only achieves a 60\% accuracy on average. There are questions for which it misses out even after we provide similar exemplars.  The results for domain-specific questions with an average accuracy of 55\% show that giving it access to functions with similar functionality confuses GPT and it tends to rely heavily on functions from a single data source leading to diminished performance. 

Finally, an error analysis was conducted to gain knowledge of GPT's performance nuances and areas for improvement. The discrepancies in errors made in each domain highlight the difference in the data structure and the nature of data returned for each of the domains. Through our analysis, we also identify some special corner cases where GPT errs. The "Single Character Parameter Value" error is one of them where GPT struggles on questions that ask for details for an entity based on some letter yet related to another entity explicitly mentioned in the question. The "Missing Non Optional Parameter" is another error where GPT does not fill in the required parameter but rather fills in the optional ones which seem logically correct when access is given to only one super function. 

Overall, this function calling capability, a pivotal step towards achieving state-of-the-art tool-augmented LLMs is a significant addition, as GPT can demonstrate a great ability to use external APIs to augment its capabilities. However, there is still room for improvement in terms of reliability and consistency of usage. The token limit poses a significant challenge and limits the number of functions that GPT can access as well as limits the possibility of solving complex tasks which may require multiple function calls. There also remains a chance even though small, where GPT does not make proper API calls or does not adhere to the API documentation. Finally, the art of judiciously using the external source is not something GPT has been fine-tuned to achieve.


# Code Structure

This repository has as its main objectives the reproducibility of the experiments, the transparency of the results, and the option to use our Custom API's setup for the Geo Domain and Music Domain respectively, to facilitate future work in similar directions. The "Ground Truth.xlsx" shows the ground truth i.e. the correct answer and correct function call for each question. The "Error Analysis and Results.xlsx" file gives an overview of the results as well as the errors made for each different setup. The structure of the two folders resources and helpers are described below.

## resources
This folder consists of all the resources to reproduce the experiments. The data folder consists of all the result files of our experiments carried out while the Python Notebooks folder consists of Python notebooks used to carry out the experiments. There is a notebook for each different prompt and function description setup used for each question set.  The structure of each notebook is almost the same, where the prompt template and all the accessible functions for GPT for a particular setup for a question set are defined at the top. Next, there are two subsections, one each for different functions accessible for that particular setup i.e. access to either a superfunction or multiple subfunctions.  The naming convention for each of the results and notebooks is self-explanatory, however, they are different from the ones mentioned in the thesis report. The table below points out which one refers to which. 


### Correspondence between Results and Thesis Naming Conventions 

| Name |	Same as |
| ------------| ------------|
| Easy Questions       | Single Function Call Questions |
| Trick Questions	| Reasoning Questions |
|	Common Questions | Common Knowledge Questions |
| Hard Questions | Multiple Function Call Questions |
| Prompt 1 | Instruct Prompt |
| Prompt 2 | Cost Awarness Prompt |
| Prompt 4 | Few-Shot CoT Prompt |
| Prompt 5 | Dual-Database Prompt |

## helpers
The helpers consist of Python files to replicate our Custom Api Setup and a file that contains helper functions for running the function calling process.
- langchainhelpers - This file consists of a custom output parser to parse the function call from GPT and functions to run an LLM chain once or multiple times. These functions are used to communicate with GPT and run the funcion calling process for each question based on the number of function calls required to answer the question.
- openstreetmaps - This file contains all functions to retrieve, parse, and structure the data retrieved Open StreetMaps.
- dbpedia - This file contains all functions to retrieve, parse, and structure the data from DBpedia. 
- geodata - This file contains all functions with basic descriptions part of Geo Api Bundle setup which combine data from Open Street Maps and DBpedia.
- geodatarefined -  Same as the above but the functions have advanced descriptions.
- musicbrainz - This file contains all functions with basic descriptions part of our Music Api Bundle setup based on the MusicBrainz API as well as other related functions to retrieve, parse, and structure data from MusicBrainz. 
- musicbrainzrefined -  Same as the above but the functions have advanced descriptions.
- spotify - This file contains all functions with advanced descriptions part of our Music Api Bundle setup based on the Spotify API as well as other related functions to retrieve, parse, and structure data from MusicBrainz.

# Requirements 

To reproduce the experiments you would need API access to Spotify API and Open AI API. The API access for Open AI is paid, however, every new user gets a 5-dollar credit. More information on how to set up the access key can be found here https://platform.openai.com/docs/quickstart?context=python. For the API access to Spotify, we refer to this article https://medium.com/@maxtingle/getting-started-with-spotifys-api-spotipy-197c3dc6353b to set up the credentials. Once you have access to both, you need to set them in the keys.env file in the helpers folder. To use the MusicBrainz API and Open Street Maps API responsibly, we also suggest updating the other 4 variables in the same file. 

Finally, we also suggest adding the path of the locally cloned repository to your PYTHONPATH environment variable so that the helpers package can be loaded anywhere. Otherwise, you would need to copy and paste the helpers folders into the Python_Notebooks to load helpers without any issues and run the experiments.
















