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
