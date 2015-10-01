select name_en, name, description_en, description, requirements_en, requirements, learning_goals_en, learning_goals, intended_audience_en, intended_audience, promotion_media_content_id_en, promotion_media_content_id from courses_course;
select title_en, title, body_en, body from courses_staticpage;
select title_en, title from courses_unit;
select title_en, title, teacher_comments_en, teacher_comments, supplementary_material_en, supplementary_material, media_content_id_en, media_content_id from courses_knowledgequantum;
select solution_text_en, solution_text from courses_question;
select solution_en, solution, text_en, text, feedback_en, feedback from courses_option;

select title_en, title, description_en, description from badges_badgebycourse;

select description_en, description from peerreview_peerreviewassignment;
select title_en, title, description_en, description, description_score_1_en, description_score_1, description_score_2_en, description_score_2, description_score_3_en, description_score_3, description_score_4_en, description_score_4, description_score_5_en, description_score_5 from peerreview_evaluationcriterion;