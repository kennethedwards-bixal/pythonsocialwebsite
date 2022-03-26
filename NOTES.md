## 1
You have added two additional fields—password and password2—for users to set their password and confirm it. You have defined a clean_password2() method to check the second password against the first one and not let the form validate if the passwords don't match. This check is done when you validate the form by calling its is_valid() method. You can provide a clean_<fieldname>() method to any of your form fields in order to clean the value or raise form validation errors for a specific field. Forms also include a general clean() method to validate the entire form, which is useful to validate fields that depend on each other. In this case, you use the field-specific clean_password2() validation instead of overriding the clean() method of the form. This avoids overriding other field-specific checks that the ModelForm gets from the restrictions set in the model (for example, validating that the username is unique).

## 2
When you have to deal with user accounts, you will find that the user model of the Django authentication framework is suitable for common cases. However, the user model comes with very basic fields. You may wish to extend it to include additional data. The best way to do this is by creating a profile model that contains all additional fields and a one-to-one relationship with the Django User model.
A one-to-one relationship is similar to a ForeignKey field with the parameter unique=True. The reverse side of the relationship is an implicit one-to-one relationship with the related model instead of a manager for multiple elements. From each side of the relationship, you retrieve a single related object.

## 3

You use the login_required decorator because users have to be authenticated to edit their profile. In this case, you are using two model forms: UserEditForm to store the data of the built-in user model and ProfileEditForm to store the additional profile data in the custom Profile model. To validate the submitted data, you execute the is_valid() method of both forms. If both forms contain valid data, you save both forms, calling the save() method to update the corresponding objects in the database.

## 4
 user: This indicates the User object that bookmarked this image. This is a foreign key field because it specifies a one-to-many relationship: a user can post multiple images, but each image is posted by a single user. You use CASCADE for the on_delete parameter so that related images are also deleted when a user is deleted.
• title: A title for the image.
• slug: A short label that contains only letters, numbers, underscores, or
hyphens to be used for building beautiful SEO-friendly URLs.
• url: The original URL for this image.
• image: The image file.
• description: An optional description for the image.
• created: The date and time that indicate when the object was created in the database. Since you use auto_now_add, this datetime is automatically set when the object is created. You use db_index=True so that Django creates an index in the database for this field.

Database indexes improve query performance. Consider setting db_index=True for fields that you frequently query using filter(), exclude(), or order_by(). ForeignKey fields or fields with unique=True imply the creation of an index. You can also use Meta.index_together or Meta.indexes to create indexes for multiple fields. You can learn more about database indexes at https://docs.djangoproject.com/en/3.0/ref/ models/options/#django.db.models.Options.indexes.

## 5
When you define a ManyToManyField, Django creates an intermediary join table using the primary keys of both models. The ManyToManyField can be defined in either of the two related models.
As with ForeignKey fields, the related_name attribute of ManyToManyField allows you to name the relationship from the related object back to this one. The ManyToManyField fields provide a many-to-many manager that allows you to retrieve related objects, such as image.users_like.all(), or get them from
a user object, such as user.images_liked.all().

## 6

You override the save() method, keeping the parameters required by ModelForm. The preceding code can be explained as follows:
1. You create a new image instance by calling the save() method of the form with commit=False.
2. You get the URL from the cleaned_data dictionary of the form.
3. You generate the image name by combining the image title slug with the
original file extension.
4. You use the Python urllib module to download the image and then call the save() method of the image field, passing it a ContentFile object that is instantiated with the downloaded file content. In this way, you save the file to the media directory of your project. You pass the save=False parameter to avoid saving the object to the database yet.
5. In order to maintain the same behavior as the save() method you override, you save the form to the database only when the commit parameter is True.
In order to use the urllib to retrieve images from URLs served through HTTPS, you need to install the Certifi Python package. Certifi is a collection of root certificates for validating the trustworthiness of SSL/TLS certificates.

## 7

In the preceding code, you use the login_required decorator for the image_create view to prevent access for unauthenticated users. This is how this view works:
1. You expect initial data via GET in order to create an instance of the form. This data will consist of the url and title attributes of an image from an external website and will be provided via GET by the JavaScript tool that you will create later. For now, you just assume that this data will be there initially.
2. If the form is submitted, you check whether it is valid. If the form data is valid, you create a new Image instance, but prevent the object from being saved to the database yet by passing commit=False to the form's save() method.
3. You assign the current user to the new image object. This is how you can know who uploaded each image.
4. You save the image object to the database.
5. Finally, you create a success message using the Django messaging framework and redirect the user to the canonical URL of the new image. You haven't yet implemented the get_absolute_url() method of the Image model; you will do that later.


## 8
In the preceding code, you retrieve the user model by using the generic function get_user_model(), which is provided by Django. You use the add_to_class() method of Django models to monkey patch the User model. Be aware that using add_to_class() is not the recommended way of adding fields to models. However, you take advantage of using it in this case to avoid creating a custom user model, keeping all the advantages of Django's built-in User model.

You also simplify the way that you retrieve related objects using the Django
ORM with user.followers.all() and user.following.all(). You use the intermediary Contact model and avoid complex queries that would involve additional database joins, as would have been the case had you defined the relationship in your custom Profile model. The table for this many-to-many relationship will be created using the Contact model. Thus, the ManyToManyField, added dynamically, will not imply any database changes for the Django User model.

Keep in mind that, in most cases, it is preferable to add fields to the Profile
model you created before, instead of monkey patching the User model. Ideally, you shouldn't alter the existing Django User model. Django allows you to use custom user models. If you want to use your custom user model, take a look at
the documentation at https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#specifying-a-custom-user-model.

Note that the relationship includes symmetrical=False. When you define a ManyToManyField in the model creating a relationship with itself, Django forces the relationship to be symmetrical. In this case, you are setting symmetrical=False to define a non-symmetrical relationship (if I follow you, it doesn't mean that you automatically follow me).

When you use an intermediary model for many-to-many relationships, some of the related manager's methods are disabled, 
such as add(), create(), or remove(). You need to create or delete instances of the intermediary model instead.


## Many2Many
The related managers, rel_from_set and rel_to_set, will return a QuerySet for the Contact model. In order to access the end side of the relationship from the User model, it would be desirable for User to contain a ManyToManyField, as follows:
   - following = models.ManyToManyField('self', through=Contact, related_name='followers', symmetrical=False)
In the preceding example, you tell Django to use your custom intermediary model for the relationship by adding through=Contact to the ManyToManyField. This
is a many-to-many relationship from the User model to itself; you refer to 'self' in the ManyToManyField field to create a relationship to the same model.


When you need additional fields in a many-to-many relationship, create a custom model with a 
ForeignKey for each side of the relationship. Add a ManyToManyField in one of the related models
and indicate to Django that your intermediary model should be used by including it in the through parameter.

## 9

You have changed the create_action() function to avoid saving duplicate actions and return Boolean to tell you whether the action was saved. This is how you avoid duplicates:
• First, you get the current time using the timezone.now() method provided by Django. This method does the same as datetime.datetime.now() but returns a timezone-aware object. Django provides a setting called USE_TZ
to enable or disable timezone support. The default settings.py file created using the startproject command includes USE_TZ=True.
• You use the last_minute variable to store the datetime from one minute ago and retrieve any identical actions performed by the user since then.
• You create an Action object if no identical action already exists in the last minute. You return True if an Action object was created, or False otherwise.


## 10
In the preceding view, you retrieve all actions from the database, excluding the ones performed by the current user. By default, you retrieve the latest actions performed by all users on the platform. If the user is following other users, you restrict the query to retrieve only the actions performed by the users they follow. Finally,
you limit the result to the first 10 actions returned. You don't use order_by() in the QuerySet because you rely on the default ordering that you provided in the Meta options of the Action model. Recent actions will come first since you set ordering = ('-created',) in the Action model.

## 11
Django offers a QuerySet method called select_related() that allows you to retrieve related objects for one-to-many relationships. This translates to a single, more complex QuerySet, but you avoid additional queries when accessing the related objects. The select_related method is for ForeignKey and OneToOne fields. It works by performing a SQL JOIN and including the fields of the related object in the SELECT statement.

You use user__profile to join the Profile table in a single SQL query. If you call select_related() without passing any arguments to it, it will retrieve objects from all ForeignKey relationships. Always limit select_related() to the relationships that will be accessed afterward.

Using select_related() carefully can vastly improve execution time.

select_related() will help you to boost performance for retrieving related objects in one-to-many relationships. However, select_related() doesn't work for many- to-many or many-to-one relationships (ManyToMany or reverse ForeignKey fields). Django offers a different QuerySet method called prefetch_related that works
for many-to-many and many-to-one relationships in addition to the relationships supported by select_related(). The prefetch_related() method performs
a separate lookup for each relationship and joins the results using Python. This method also supports the prefetching of GenericRelation and GenericForeignKey.