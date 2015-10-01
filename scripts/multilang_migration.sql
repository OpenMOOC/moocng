update courses_course set name_en = name, description_en = description, requirements_en = requirements, learning_goals_en = learning_goals, intended_audience_en = intended_audience, promotion_media_content_id_en = promotion_media_content_id;
update courses_staticpage set title_en = title, body_en = body;
update courses_unit set title_en = title;
update courses_knowledgequantum set title_en = title, teacher_comments_en = teacher_comments, supplementary_material_en = supplementary_material, media_content_id_en = media_content_id;
update courses_question set solution_text_en = solution_text;
update courses_option set solution_en = solution, text_en = text, feedback_en = feedback;

update badges_badgebycourse set title_en = title, description_en = description;

update peerreview_peerreviewassignment set description_en = description;
update peerreview_evaluationcriterion set title_en = title, description_en = description, description_score_1_en = description_score_1, description_score_2_en = description_score_2, description_score_3_en = description_score_3, description_score_4_en = description_score_4, description_score_5_en = description_score_5;