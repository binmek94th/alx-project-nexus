def build_comment_tree(comments):
    """
    Builds a tree structure from a flat list of comments.
    This function organizes comments into a hierarchical structure based on their parent-child relationships.
    Each comment can have multiple children, and the root comments (those without a parent) are
    returned as the top-level comments in the tree.
    :param comments: List of Comment objects to be organized into a tree structure.
    :return:
    """
    comment_dict = {comment.id: comment for comment in comments}
    root_comments = []

    for comment in comments:
        setattr(comment, "_children", [])

    for comment in comments:
        if comment.comment_id:
            parent = comment_dict.get(comment.comment_id)
            if parent:
                parent._children.append(comment)
        else:
            root_comments.append(comment)

    return root_comments