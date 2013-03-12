Mongo Structure
===============

MongoDB is used to store all user activity.

 These activities include:

* Watches videos (activity collection)
* Answers (answers collection)


Activity Collection
*******************

The collection name is **activity**.

This collection store user watches videos for every course.

This collection have one object per user.


Object Structure
----------------

* **_id**: Native mongo ObjectId
* **user**: (Integer) *User id* in moocng.
* **courses**: (String) Object where every property is one *Course id* in
  moocng.

  * **kqs**: (List of Strings) Every item in list is one *KnowledQuantum id*
    (KQ) in moocng. If a KQ is in this list then this KQ video has been viewed.


Example
-------

.. code-block:: javascript

    {
        "_id" : ObjectId("503f31d5c7ace528b1545baab"),
        "courses" : {
            "1" : {
                "kqs" : [
                    "2",
                    "6",
                    "8",
                    "144",
                    "150",
                    "153",
                    "157",
                    "147",
                    "77",
                    "184"
                ]
            },
            "8" : {
                "kqs" : [
                    "46",
                    "47",
                    "48",
                    "49",
                    "50",
                    "51",
                    "52"
                ]
            },
            "2" : {
                "kqs" : [
                    "159",
                    "40",
                    "41",
                    "85",
                    "161",
                    "94",
                    "158",
                    "160"
                ]
            },
        },
        "user": 2
    }


Answers Collection
******************

The collection name is **answers**.

This collection store user answers for every *Question*.

This collection have one object per user.


Example
-------

.. code-block:: javascript

   {
       "_id" : ObjectId("5045dc8ec7ace54264704216"),
       "user" : 1,
       "questions" : {
           "15" : {
               "date" : "2012-09-04T12:09:53.095Z",
               "replyList" : [
                   {
                       "option" : "25",
                       "value" : false
                   },
                   {
                       "option" : "26",
                       "value" : true
                   }
               ]
           },
           "22" : {
               "date" : "2012-10-19T11:04:39Z",
               "replyList" : [
                   {
                       "option" : "60",
                       "value" : false
                   },
                   {
                       "option" : "115",
                       "value" : false
                   },
                   {
                       "option" : "114",
                       "value" : true
                   }
               ]
           },
       }
   }


Object Structure
----------------

* **_id**: Native mongo ObjectId
* **user**: (Integer) *User id* in moocng.
* **questions**: (Object) Object where every object key is a *Question id*
  (string) is one question answered by user.

  * **date**: (datetime) ISO DateTime Format, just last user answer.
  * **replyList**: (Object List): Every Object is one *Option* with user
    answer.

    * **option**: (String) *Option id* in moocng.
    * **value**: (Any) user response value (binary, string, ...)


Peer Review Submissions Collection
**********************************

The collection name is **peer_review_submissions**.

This collection store peer review user submissions for every *KnowledQuantum*
with *PeerReviewAssignement*.

This collection have one object per user submission.


Example
-------

.. code-block:: javascript

   {
       "_id" : ObjectId("513df5e9ac15dd081146d479"),
       "author" : 1,
       "author_reviews" : 1,
       "text" : "Text from submission from user 1",
       "file" : "513e0dbfc2fc058ab13fd894",
       "created" : "2013-03-11T10:19:05.713189",
       "reviewers" : [
           2
       ],
       "reviews" : 1,
       "course" : 1,
       "unit" : 1
       "kq" : 1,
       "assigned_to": 3
   }


Object Structure
----------------

* **_id**: Native mongo ObjectId
* **author**: (Integer) Submission author *User id* in moocng.
* **author_reviews**: (Integer) Reviews to this *Asignement* from this user.
* **text**: (String) Text given from student.
* **file**: (String) link to file uploaded by user, or a ID in s3.
* **created**: (datetime) String ISO DateTime Format.
* **reviewers**: (List): Every Object is one *User id* who has reviewed this
  submission.
* **reviews**: (Integer) Count, how many times has been reviewed this review by
  others.
* **course**: (Integer): *Course id*
* **unit**: (Integer): *Unit id*
* **kq**: (Integer): *KnowledQuantum id* is related to *PeerReviewAssignement*.
* **assigned_to**: (Integer) One *User id* from user who has been assigned to
  review this assignement. This user can't be present in **reviewers** until he
  finish the review.


Peer Review Reviews Collection
**********************************

The collection name is **peer_review_reviews**.

This collection store user reviews for assignement submissions.

This collection have one object per user review.


Example
-------

.. code-block:: javascript

   {
       "_id" : ObjectId("513dfd9aac15dd0c529f4df9"),
       "author" : 2,
       "reviewer" : 1,
       "comment" : "This is text about submission from user reviewer",
       "submission_id" : ObjectId("513df5e9ac15dd081146d479"),
       "created" : "2013-03-11T10:51:54.172189",
       "criteria" : [
           [1, 3],
           [2, 2],
           [3, 5]
       ],

       "course" : 1,
       "unit" : 1
       "kq" : 1,
   }



Object Structure
----------------

* **_id**: Native mongo ObjectId
* **author**: (Integer) Submission author *User id* in moocng.
* **reviewer**: (Integer) *User id* from reviewer user.
* **comment**: (String) Text given from reviewer.
* **submission_id**: Native mongo ObjectId from relate Submission.
* **created**: (datetime) String ISO DateTime Format, user .
* **criteria**: (List): List of List, every child has the value per criteria.
  * **first item**: (Integer) This is *criteria_id*.
  * **second item** (Integer) This is the value given by reviewer.
* **course**: (Integer): *Course id*.
* **unit**: (Integer): *Unit id*.
* **kq**: (Integer): *KnowledQuantum id* is related to *PeerReviewAssignement*.
