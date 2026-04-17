from __future__ import annotations


def get_cards_query() -> str:
    return """
    query GetPipeCards($pipe_id: ID!) {
      cards(pipe_id: $pipe_id, first: 200) {
        edges {
          node {
            id
            title
            created_at
            updated_at
            due_date
            finished_at
            done
            current_phase {
              id
              name
            }
            labels {
              id
              name
            }
            assignees {
              id
              name
              email
            }
            fields {
              name
              value
            }
          }
        }
      }
    }
    """


def get_organization_pipes_query() -> str:
    return """
    query GetOrganizationPipes($organization_id: ID!) {
      organization(id: $organization_id) {
        id
        name
        pipes {
          id
          name
        }
      }
    }
    """


def get_pipe_metadata_query() -> str:
    return """
    query GetPipeMetadata($pipe_id: ID!) {
      pipe(id: $pipe_id) {
        id
        name
        start_form_fields {
          id
          label
          type
        }
        users {
          id
          name
        }
        phases {
          id
          name
        }
      }
    }
    """


def create_card_mutation() -> str:
    return """
    mutation CreateCard($input: CreateCardInput!) {
      createCard(input: $input) {
        card {
          id
          title
          due_date
          current_phase {
            id
            name
          }
        }
      }
    }
    """


def move_card_to_phase_mutation() -> str:
    return """
    mutation MoveCardToPhase($input: MoveCardToPhaseInput!) {
      moveCardToPhase(input: $input) {
        card {
          id
          current_phase {
            id
            name
          }
        }
      }
    }
    """


def update_card_field_mutation() -> str:
    return """
    mutation UpdateCardField($input: UpdateCardFieldInput!) {
      updateCardField(input: $input) {
        card {
          id
        }
      }
    }
    """


def update_card_assignee_mutation() -> str:
    return """
    mutation UpdateCardAssignee($input: UpdateCardInput!) {
      updateCard(input: $input) {
        card {
          id
          assignees {
            id
            name
          }
        }
      }
    }
    """
